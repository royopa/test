from py_init import *

def SRVfunction(t,z,v,w,k,eta,s,thet,rho):
    '''
    Equation 22 of 'A New Simple Approach for Constructing Implied Volatility Surfaces'
    :param t: 1 x nT
    :param z: nZ x 1
    :param v: nZ x nT
    :param w:
    :param k:
    :param eta:
    :param s:
    :param thet:
    :param rho:
    :return:
    '''

    fcn=(1+k*t)*v**2+(w**2*exp(-2*eta*t)*t**(3/2)*z)*v\
        -((k*thet-w**2*exp(-2*eta*t))*t+s**2+2*rho*w*s*exp(-eta*t)*sqrt(t)*z+w**2*exp(-2*eta*t)*t*z**2)
    return fcn


from old import mSSM as ssm
import mUtilGPU as gu
import mGPUlib as gpu
class surfFit(ssm.mSSM):

    def __init__(self,a0,P0,volData):
        ssm.mSSM.__init__(self,a0,P0)
        self.volData=volData
        self.nA=6

    def H(self,alp_):
        #consider the needed tranforms in alpha
        return SRVfunction(self.volData.t,self.volData.z,self.volData.v,alp_[0,:,:],alp_[1,:,:],alp_[2,:,:]
                           , alp_[3, :, :],alp_[4,:,:],alp_[5,:,:])

    def log_py(self, y_, alp_, t):
        """
        Redefine. Default: use gaussian distribution assuming non-linear model
        """
        sig1 = self.PSI.sig #gu.exp(alp_)
        #        sig1= gu.exp(gu.maximum(gu.minimum(alp,706),-706) )*self.PSI.sig
        #        else:
        #           H1=M.H
        h=self.H(alp_)
        py1 = -gu.log(sig1 * np.sqrt(2 * np.pi)) - 0.5 * (((y_-h)/ sig1) ** 2)

        return py1

    # def Py_alp(self, y_, alp_, t):
    #     """
    #     Redefine. Default: use gaussian distribution assuming non-linear model
    #     """
    #
    #     seas1 = self.getSeasonality(alp_.shape[-1])
    #     seas1 = uu.ap1(seas1, -(len(alp_.shape) - len(seas1.shape)))
    #
    #     alp1 = gu.bsxfun(alp_, seas1, 'plus')
    #     sig11 = gu.exp(alp1 * 0.5 + np.log(self.PSI.sig))
    #     sig1_tail = gu.exp(alp1 * 0.5 + np.log(self.PSI.sig_tail))
    #
    #     py1 = gu.skellamcdf(y_, self.PSI.mu, sig11)
    #     py1_tail = gu.skellamcdf(y_, self.PSI.mu, sig1_tail)
    #
    #     w0 = np.abs(self.PSI.w0)
    #     w_tail = np.abs(self.PSI.w_tail)
    #     M = np.maximum(w_tail + w0, 1)
    #     py = w0 * py1 + w_tail * py1_tail + 0.5*(y_ == 0) * (1 - (w_tail + w0) / M) +(y_ > 0) * (1 - (w_tail + w0) / M)
    #     assert (not (np.any(np.isnan(py)) or np.any(np.isinf(py))))
    #
    #     return py

    def simulate(self, nT):
        """
        simulate stock vol
        """
        # nY=1
        nY = self.nY
        nA = self.PSI.P0.shape[0]
        a0_rnd, eta_rnd, eps_rnd = self.genRndDist(1, nT)

        eta_rnd = eta_rnd[:, 0, :]
        a = np.empty([nA, nT + 1])
        y = np.empty([nA, nT])
        a[:, 0] = a0_rnd[:, 0]
        #sQ_ = gu.chol(self.PSI.Q)



        for t in range(nT):
            M = self.M(a[:, t:t + 1], t)
            sQ_ = gu.chol(M.Q[:,:,0])
            a[:, t + 1] = M.T[:, 0] + gu.multiprod(sQ_, eta_rnd[:, t], [0, 1], [0])


        seas1 = uu.ap1(self.getSeasonality(a.shape[1]),-1)


        pmf0 = np.exp(gu.logmskellampdf1(gu.ap1(self.ys, 1), self.PSI.mu, np.exp(a + seas1) * self.PSI.sig, gam=self.PSI.gam))
        pmf1 = np.exp(gu.logmskellampdf1(gu.ap1(self.ys, 1), self.PSI.mu, np.exp(a + seas1) * self.PSI.sig_tail,
                                         gam=np.atleast_1d(0)))

        pmf=pmf0*(1-self.PSI.w_tail)+pmf1*self.PSI.w_tail
        y = gu.randgenM(self.ys, pmf, 1).astype(np.float64)

        return y, a, eps_rnd, eta_rnd

    def getFittedOpt(self, y,opts1 ):
        # a_mode = (np.log(pd.DataFrame(y.T).rolling(100, center=True).std()) - np.log(self.PSI.sig)).values
        # a_mode[:100] = a_mode[99]
        # a_mode[-100:] = a_mode[-100]
        # a_mode = a_mode.T

        opts=copy.deepcopy(opts1)
        opts.max_a = np.array([20])
        k_ = 10
        opts.par1.b = 1/k_
        nT = y.shape[1]
        opts.par1.C = np.asfortranarray(gu.repmat(np.eye(self.nA), [1, 1, nT])) / k_
        opts.par1.iC = opts.par1.C * k_**2
        opts.par0 = opts.par1
        opts.a_0 = opts.a_1
        opts.z, opts.h = gu.GaussHermite(12)
        return opts


    def log_py_pa_t(self,y_,alp,a0_rnd,t):

        alpL = gu.cat(2, [gu.ap1(a0_rnd, 1) * 1, alp[:, :, :-1]])

        alp0=alpL
        # sig1=self.PSI.sig

        exp=gu.exp
        log=gu.log

        log_py=gu.sum(self.log_py(y_, alp, t),0)
        psi=1#self.PSI.psi #ones
        q=gu.ap1(np.diag(self.PSI.Q),2)
        log_py_pa = log_py - gu.sum(((alp - psi * alp0) **2) / q / 2 - log(q)/2,0)
        log_py_pa =gu.ap1(log_py_pa,-1)

        return gpu.gather(log_py_pa)

    def d_log_py_pa_t(self,y_,alp,a0_rnd,t,log_py_pa_t=None):
        # sig0,sig1,w1,psi,q,qdummy,beta
        alpL = gu.cat(2, [gu.ap1(a0_rnd, 1) * 1, alp[:, :, :-1]])
        alp0=alpL
        q=gu.ap1(np.diag(self.PSI.Q),2)
        psi=1
        sig1 = self.PSI.sig
        h=self.H(alp)

        dp_d_phi=np.empty((self.PSI.Q.shape[0]+1,)+alp.shape[1:])

        dp_d_phi[0, :, :] = gpu.gather(-1/sig1 +(y_-h)**2/sig1**3 )

        #q
        dp_d_phi[1:, :, :] =  gpu.gather((alp - alp0*psi)**2/(2*q**2)-1/q/2)
        return dp_d_phi






    def d2_log_py_pa_st(self,y_,alp,a0_rnd,t,log_py_pa_t=None,d_log_py_pa_t=None):

        alpL = gu.cat(2, [gu.ap1(a0_rnd, 1) * 1, alp[:, :, :-1]])
        alp0=alpL
        q=gu.ap1(np.diag(self.PSI.Q),2)
        psi=1
        sig1 = self.PSI.sig
        h=self.H(alp)

        d2p_d_phi=np.zeros((self.PSI.Q.shape[0]+1,self.PSI.Q.shape[0]+1)+alp.shape[1:-1])

        d2p_d_phi[0, 0, :] = gpu.gather(sig1**(-2) -3*(y_-h)**2/sig1**4 )

        A=-(alp - alp0*psi)**2/q**3+1/q**2/2
        for i in range(self.nA):
            d2p_d_phi[i, i, :] =gpu.gather(gu.sum(A,-1))[i,:]



        return d2p_d_phi


    def setPSIwithX(self,x):
        self.PSI.sig = np.maximum(np.abs(np.atleast_1d(x[0])),1e-15)
        self.PSI.Q = np.maximum(np.abs(np.diag(x[1:])),1e-15)

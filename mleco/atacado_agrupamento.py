# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 09:50:44 2019

@author: marcgut
"""
import shelve




def make_groups():
    """Essa função faz os grupos para projeção. As listas só precisam ser compostas na mão para os itens
    que NÃO POSSUEM correspondência direta com o índice (mas que se quer utilizar de qualquer jeito).
    Caso o item tenha correspondência direta com algum item do monitor, colocar em make_ref()."""
       
    groups = {}
    groups[('frutas', '1106')] = [
                          'ceagesp_CAJU__A', 'ceagesp_CAJU__B', 'ceagesp_CARAMBOLA__',
                          'ceagesp_COCOVERDE__', 'ceagesp_FIGO__A', 'ceagesp_FIGO__B',
                          'ceagesp_FRUTADOCONDE__910FRUTOS', 'ceagesp_FRUTADOCONE__12FRUTOS',
                          'ceagesp_FRUTADOCONDE__15FRUTOS', 'ceagesp_FRUDADOCONDE__18FRUTOS',
                          'ceagesp_GRAVIOLA__', 'ceagesp_GOIABA_VERMELHA_9FRUTOS', 
                          'ceagesp_GOIABA_VERMELHA_12FRUTOS',
                          'ceagesp_GOIABA_VERMELHA_18FRUTOS', 'ceagesp_GOIABA_BRANCA_9FRUTOS',
                          'ceagesp_MARACUKA_AZEDO_A',
                          'ceagesp_MELAO_AMARELO_67FRUTOS',
                          'ceagesp_MELAO_AMARELO_89FRUTOS', 'ceagesp_MELAO_AMARELO_1214FRUTOS',
                          'ceagesp_ROMA__',
                          'ceagesp_AMEIXAESTRANG__',
                          'ceagesp_KIWIESTRANG__', 'ceagesp_MACAESTRANG_REDDEL_80163FRUTOS',
                          'ceagesp_MACAESTRANG_GRANNYSMITH_80162FRUTOS',
                          'ceagesp_NECTARIANAESTRA__', 
                          'ceagesp_LIMA_PERSIA_A910DZ', 'ceagesp_LIMA_PERSIA_B1315DZ',
                          'ceagesp_LIMA_PERSIA_C1824DZ', 'ceagesp_LIMAO_TAITI_A2127DZ',
                          'ceagesp_LIMAO_TAITI_B3238DZ', 'ceagesp_LIMAO_TAITI_C4045DZ',
                          'ceagesp_MACANACIONAL_FUJI_80150FRUTOS', 'ceagesp_MACANACIONAL_FUJI_163180FRUTOS',
                          'ceagesp_MACANACIONAL_GALA_80150FRUTOS', 'ceagesp_MACANACIONAL_GALA_163180FRUTOS',
                          'prohort_ABACATE']

    groups[('tuberculos', '1103')] = [
                              'ceagesp_BATATADOCE_AMARELA_EXTRAAA', 'ceagesp_BATATADOCE_AMARELA_EXTRAA',
                              'ceagesp_BATATADOCE_AMARELA_EXTRA', 'ceagesp_BATATADOCE_ROSADA_EXTRAAA',
                              'ceagesp_BATATADOCE_ROSADA_EXTRAA', 'ceagesp_BATATADOCE_ROSADA_EXTRA',
                              'ceagesp_BERINJELA_CONSERVA_EXTRA',
                              'ceagesp_QUIABO_LISO_EXTRAAA', 'ceagesp_QUIABO_LISO_EXTRAA',
                              'ceagesp_QUIABO_LISO_EXTRA']

    groups[('hortaliças', '1105')] = ['ceagesp_AGRIAO__EXTRA', 'ceagesp_AGRIAO__ESPECIAL',
                              'ceagesp_AGRIAO__PRIMEIRA',
                              'ceagesp_CEBOLINHA__EXTRA', 'ceagesp_CEBOLINHA__ESPECIAL',
                              'ceagesp_CEBOLINHA__PRIMEIRA', 'ceagesp_CHICORIA__',
                              'ceagesp_AGRIAO__HIDROPONICO', 'ceagesp_ERVADOCE__EXTRA',
                              'ceagesp_ERVADOCE__ESPECIAL', 'ceagesp_ERVADOCE__PRIMEIRA',
                              'ceagesp_ESPINAFRE__ESPECIAL', 'ceagesp_ESPINAFRE__PRIMEIRA',
                              ]
    
    groups[('aves', '1110')] = []
    
    groups[('pescados', '1108')] = []#['ceagesp_PINTADO__']

    groups[('açucares', '1104')] = ['bbg_sugar']
    
    groups[('cereais', '1101')] = []
    
    groups[('carnes', '1107')] = ['cepea_bezerro_ms_brl', 'cepea_boi_brl', 'cepea_boi_prazo_brl',
                            'bbg_live_cattle',
                           'bbg_feeder_cattle', 'bbg_lean_hogs', 'bbg_boi futuro',
                           ]
    
    groups[('bebidas', '1114')] = ['bbg_coffee']
    
    groups[('leites', '1111')] = []
    
    groups[('conserva', '1115')] = []
    
    groups[('condimentos', '1116')] = []
    
    groups[('farinhas', '1102')] = []
    
    groups[('oleos', '1113')] = ['bbg_soy_oil']
    
    groups[('industrializados', '1109')] = ['cepea_bezerro_ms_brl', 'cepea_boi_brl', 'cepea_boi_prazo_brl',
                                            'cepea_suinos_mg', 'cepea_suinos_pr', 'cepea_suinos_rs',
                                            'cepea_suinos_sc', 'cepea_suinos_sp','bbg_live_cattle',
                                            'bbg_feeder_cattle', 'bbg_lean_hogs', 'bbg_boi futuro',
                                            'bbg_carcaca', 'bbg_dianteiro', 'bbg_traseiro']
    
    groups[('panificados', '1112')] = ['cepea_trigo_pr_brl', 'cepea_trigo_rs_brl']
    
    for ituple in groups:
        groups[ituple] = groups[ituple] + list_itens(ituple[1])
    
    groups['commodities_gerais'] = ['cepea_milho_campinas_brl', 'cepea_milho_sp_brl',
                          'cepea_soja_paranagua_brl', 'cepea_soja_pr_brl',
                          'bbg_soy', 'bbg_corn', 'bbg_wheat']
    
    
    
    return groups
    

def make_ref():
    """Correspondência dos produtos do atacado para os respectivos itens do IPCA."""
    
    ref_itens = {}
    
    ref_itens[('tomate','1103028')] = ['ceagesp_TOMATE_SWEETGRAPE_EXTRAAA',
                                       'ceagesp_TOMATE_MADURO_EXTRAAA',
                                       'ceagesp_TOMATE_MADURO_EXTRAA', 'ceagesp_TOMATE_MADURO_EXTRA',
                                       'ceagesp_TOMATE_SALADA_EXTRAAA', 'ceagesp_TOMATE_SALADA_EXTRAA',
                                       'ceagesp_TOMATE_SALADA_EXTRA', 'ceagesp_TOMATE_OBLONGO_EXTRAAAA',
                                       'ceagesp_TOMATE_OBLONGO_EXTRAAA', 'ceagesp_TOMATE_OBLONGO_EXTRAA',
                                       'ceagesp_TOMATE_CAQUI_EXTRAAA', 'ceagesp_TOMARE_CEREJA_EXTRAAA',
                                       'ceagesp_TOMATE_HOLANDES_', 'prohort_TOMATE']
    
    
    
    ref_itens[('frango', '1110009')] = ['cepea_frango_congelado_sp_brl',
                                        'cepea_frango_resfriado_sp_brl']

    ref_itens[('ovo', '1110044')] = ['ceagesp_OVOS_BRANCO_GRANDEEMBALADO', 'ceagesp_OVOS_BRANCO_EXTRA',
                                     'ceagesp_OVOS_BRANCO_GRANDE', 'ceagesp_OVOS_BRANCO_MEDIO',
                                     'ceagesp_OVOS_BRANCO_PEQUENO', 'ceagesp_OVOS_BRANCO_EXTRAEMBALADO',
                                     'ceagesp_OVOS_VERMELHO_EXTRA','cepea_ovos_branco',
                                     'cepea_ovos_vermelho', 'prohort_OVO']
    
    ref_itens[('abacaxi', '1106003')] = ['ceagesp_ABACAXI_HAVAI_AGRAUDO',
                          'ceagesp_ABACAXI_HAVAI_BMEDIO', 'ceagesp_ABACAXI_HAVAI_CMIUDO',
                          'ceagesp_ABACAXI_PEROLA_AGRAUDO',
                          'ceagesp_ABACAXI_PEROLA_CMIUDO', 'prohort_abacaxi']
    
    ref_itens[('banana-da-terra', '1106001')] = ['ceagesp_BANANA_TERRA_','ceagesp_BANANA_NANICACLIMAT_']
    
    ref_itens[('maçã', '1106017')] = ['prohort_MAÇÃ']
    
    ref_itens[('banana-prata', '1106008')] = ['ceagesp_BANANA_PRATAMG_',
                                              'ceagesp_BANANA_PRATASP_',
                                              'prohort_BANANA_PRATA']
    
    ref_itens[('banana-dagua', '1106001')] = ['ceagesp_BANANA_MACA_', 'ceagesp_BANANA_OURO_',
                                              'prohort_BANANA_NANICA']
    
    ref_itens[('manga', '1106019')] = ['ceagesp_MANGA_PALMER_12FRUTOS', 'ceagesp_MANGA_PALMER_15FRUTOS',
                                      'ceagesp_MANGA_PALMER_18FRUTOS', 'ceagesp_MANGA_TOMMYATKINS_12FRUTOS',
                                      'ceagesp_MANGA_TOMMYATKINS_18FRUTOS'] #+ from_prohort('manga')
    
    ref_itens[('maracuja', '1106020')] = ['ceagesp_MARACUJA_AZEDO_B', 'ceagesp_MARACUJA_AZEDO_C',
                          'ceagesp_MARACUJA_DOCE_8FRUTOS', 'ceagesp_MARACUJA_DOCE_10FRUTOS',
                          'ceagesp_MARACUJA_DOCE_12FRUTOS', 'ceagesp_MARACUJA_DOCE_15FRUTOS',
                          'prohort_maracuja']# + from_prohort('maracuja')
    
    ref_itens[('melancia', '1106021')] = ['ceagesp_MELANCIA_REDONCOMPRIDA_GRAUDA', 'ceagesp_MELANCIA_REDOCOMPRIDA_MEDIA',
                                          'ceagesp_MELANCIA_REDONCOMPRIDA_MIUDA',
                                          'prohort_MELANCIA']
    
    ref_itens[('morango', '1106051')] = ['ceagesp_MORANGO_COMUM_', 
                                          'ceagesp_MORANGO_CAMINHOREAL_',
                                          'prohort_MORANGO']
    
    ref_itens[('tangerina', '1106027')] = ['ceagesp_TANGERINA_MURCOT_A810DZ',
                          'ceagesp_TANGERINA_MURCOT_B1112DZ', 'ceagesp_TANGERINA_MURCOT_C1315DZ',
                          'prohort_TANGERINA']
    
    ref_itens[('uva', '1106028')] = ['ceagesp_UVA_NIAGARA_EXTRAA', 'ceagesp_UVA_NIAGARA_EXTRA', 
                          'ceagesp_UVA_NIAGARA_ESPECIAL', 'ceagesp_UVA_ITALIA_EXTRAA',
                          'ceagesp_UVA_ITALIA_EXTRA', 'ceagesp_UVA_ITALIA_ESPECIAL',
                          'ceagesp_UVA_BRASIL_EXTRAA', 'ceagesp_UVA_BRASIL_EXTRA',
                          'ceagesp_UVA_BRASIL_ESPECIAL', 'ceagesp_UVA_RUBI_EXTRAA',
                          'ceagesp_UVA_RUBI_EXTRA', 'ceagesp_UVA_BENITAKA_',
                          'ceagesp_UVA_THOMPSON_', 'prohort_UVA_RUBI', 'prohort_UVA_ITALIA',
                          'prohort_UVA_NIAGARA']
    
    ref_itens[('pera', '1106023')] = ['ceagesp_PERAESTRANG_DANJOU_',
                          'ceagesp_PERAESTRANG_PACKSTRIUMPH_',
                          'ceagesp_PERAESTRANG_WILLIAMS_', 'ceagesp_PERAESTRANG_ROCHA_',
                          'prohort_PERA']
    
    ref_itens[('laranja', '1106039')] = ['ceagesp_LARANJA_LIMA_A1013DZ', 'ceagesp_LARANJA_LIMA_B1415DZ',
                          'ceagesp_LARANJA_LIMA_C1821DZ', 'ceagesp_LARANJA_PERA_B1415DZ',
                          'ceagesp_LARANJA_PERA_C1821DZ', 'ceagesp_LARANJA_SELETA_A810DZ',
                          'ceagesp_LARANJA_SELETA_B1113DZ', 'ceagesp_LARANJA_SELETA_C1821DZ',
                          'prohort_LARANJA_PERA']
    
    ref_itens[('mamao', '1106018')] = ['ceagesp_MAMAO_FORMOSA_A', 'ceagesp_MAMAO_FORMOSA_B', 'ceagesp_MAMAO_HAVAI_12FRUTOS',
                          'ceagesp_MAMAO_HAVAI_15FRUTOS', 'ceagesp_MAMAO_HAVAI_18FRUTOS',
                          'ceagesp_MAMAO_HAVAI_21FRUTOS', 'ceagesp_MAMAO_HAVAI_2428FRUTOS',
                          'prohort_MAMAO_FORMOSA', 'prohort_MAMAO_HAVAI']
    
    ref_itens[('abobora', '1103017')] = ['ceagesp_ABOBORA_JAPONESA_', 'ceagesp_ABOBORA_SECA_',
                              'ceagesp_ABOBORA_MORANGA_', 'ceagesp_ABOBORA_PAULISTA_']
    
    ref_itens[('inhame', '1103004')] = ['ceagesp_INHAME__EXTRAA', 'ceagesp_INHAME__EXTRA',
                              'ceagesp_INHAME__ESPECIAL']
    
    ref_itens[('mandioquinha', '1103046')] = ['ceagesp_MANDIOQUINHA__EXTRAAAA', 'ceagesp_MANDIOQUINHA__EXTRAAA',
                              'ceagesp_MANDIOQUINHA__EXTRAA', 'prohort_MANDIOQUINHA']# + from_prohort('MANDIOQUINHA')
    
    ref_itens[('mandioca', '1103005')] = ['ceagesp_MANDIOCA__GRAUDA', 'ceagesp_MANDIOCA__MEDIA', 
                              'ceagesp_MANDIOCA__MIUDA']
    
    ref_itens[('cenoura', '1103044')] = ['ceagesp_CENOURACFOLHA__EXTRA',
                              'ceagesp_CENOURACFOLHA__ESPECIAL', 'ceagesp_CENOURACFOLHA__PRIMEIRA',
                              'prohort_CENOURA']
    
    
    ref_itens[('batata', '1103003')] = ['ceagesp_BATATA_COMUM_ESPECIAL',
                                        'ceagesp_BATATA_COMUM_1a2a', 'ceagesp_BATATA_COMUM_ESPECIALZINHA',
                                        'ceagesp_BATATA_BENEFCOMUM_ESPECIAL', 'ceagesp_BATATA_BENEFCOMUM_1a2a',
                                        'ceagesp_BATATA_BENEFCOMUM_ESPECIALZINHA', 'ceagesp_BATATA_BENEFLISA_ESPECIAL',
                                        'ceagesp_BATATA_LAVADA_1aESPECIALZINH', 'ceagesp_BATATA_LAVADA_BONECA',
                                        'prohort_BATATA']

    ref_itens[('cebola', '1103043')] = ['ceagesp_CEBOLA_ROXA_GRAUDA', 'ceagesp_CEBOLA_ROXA_MEDIA',
                              'ceagesp_CEBOLA_ROXA_MIUDA', 'ceagesp_CEBOLA_STACATARINA_GRAUDA',
                              'ceagesp_CEBOLA_STACATARINA_MEDIA', 'ceagesp_CEBOLA_STACATARINA_MIUDA',
                              'prohort_CEBOLA']

    ref_itens[('brocolis', '1105019')] = ['ceagesp_BROCOLOS__EXTRA',
                                          'ceagesp_BROCOLOS__ESPECIAL',
                                          'ceagesp_BROCOLOS_NINJA_',
                                          'prohort_BRÓCOLOS']

    ref_itens[('coentro', '1105004')] = ['ceagesp_COENTRO__EXTRA', 'ceagesp_COENTRO__ESPECIAL']
    
    ref_itens[('couve', '1105005')] = ['ceagesp_COUVE__EXTRA', 'ceagesp_COUVE__ESPECIAL',
                              'ceagesp_COUVE__PRIMEIRA', 'ceagesp_COUVE_BRUXELAS_EXTRA',
                              'prohort_couve']
    
    ref_itens[('alface', '1105001')] = ['ceagesp_ALFACE_CRESPA_HIDROPONICA_1type',
                              'ceagesp_ALFACE_CRESPA_HIDROPONICA_2type',
                              'ceagesp_ALFACE_CRESPA_HIDROPONICA_3type',
                              'ceagesp_ALFACE_CRESPA_HIDROPONICA_4type',
                              'ceagesp_ALFACE_CRESPA_HIDROPONICA_5type',
                              'ceagesp_ALFACE_CRESPA_HIDROPONICA_6type',
                              'ceagesp_ALFACE_CRESPA_HIDROPONICA_7type',
                              'ceagesp_ALFACE_LISA_HIDROPONICA',
                              'ceagesp_ALFACE_MIMOSA_HIDROPONICA', 'ceagesp_RUCULA__HIDROPONICA',
                              'ceagesp_ALFACE_AMERICANA_EXTRA', 'ceagesp_ALFACE_AMERICANA_ESPECIAL',
                              'ceagesp_ALFACE_AMERICANA_PRIMEIRA', 'ceagesp_ALFACE_CRESPA_EXTRA',
                              'ceagesp_ALFACE_CRESPA_ESPECIAL', 'ceagesp_CRESPA_PRIMEIRA',
                              'ceagesp_ALFACE_ROMANA_', 'ceagesp_ALFACE_LISA_EXTRA', 
                              'ceagesp_ALFACE_LISA_ESPECIAL', 'ceagesp_ALFACE_LISA_PRIMEIRA',
                              'prohort_ALFACE']
    
    ref_itens[('couve-flor', '1105006')] = ['ceagesp_COUVEFLOR__EXTRA', 'ceagesp_COUVEFLOR__ESPECIAL',
                              'ceagesp_COUVEFLOR__PRIMEIRA']
    
    ref_itens[('repolho', '1105010')] = ['ceagesp_REPOLHO_LISO_EXTRA',
                              'ceagesp_REPOLHO_ROXO_EXTRA', 'prohort_repolho']
    
#    ref_itens[('cação', '1108029')] = ['ceagesp_CACAO_CONGELADA_GRANDE']
    
#    ref_itens[('salmão', '1108075')] = ['ceagesp_SALMAO__GRANDE']
    
#    ref_itens[('pescada', '1108038')] = ['ceagesp_PESCADA__MEDIA', 'ceagesp_PESCADA__PEQUENA']
    
    ref_itens[('açúcar cristal', '1104004')] = ['cepea_acucar_santos_brl', 'cepea_acucar_sp_brl']
    
    ref_itens[('arroz', '1101002')] = ['cepea_arroz_brl']
    
    ref_itens[('figado', '1107009')] = ['bbg_carcaca', 'bbg_dianteiro', 'bbg_traseiro']
    
    ref_itens[('contra file', '1107084')] = ['bbg_carcaca', 'bbg_dianteiro', 'bbg_traseiro']
    
    ref_itens[('file mignon', '1107085')] = ['bbg_carcaca', 'bbg_dianteiro', 'bbg_traseiro']
    
    ref_itens[('chã de dentro', '1107087')] = ['bbg_carcaca', 'bbg_dianteiro', 'bbg_traseiro']
    
    ref_itens[('alcatra', '1107088')] = ['bbg_carcaca', 'bbg_dianteiro', 'bbg_traseiro']
    
    ref_itens[('patinho', '1107089')] = ['bbg_carcaca', 'bbg_dianteiro', 'bbg_traseiro']
    
    ref_itens[('lagarto redondo', '1107090')] = ['bbg_carcaca', 'bbg_dianteiro', 'bbg_traseiro']
    
    ref_itens[('lagarto comum', '1107091')] = ['bbg_carcaca', 'bbg_dianteiro', 'bbg_traseiro']
    
    ref_itens[('musculo', '1107093')] = ['bbg_carcaca', 'bbg_dianteiro', 'bbg_traseiro']
    
    ref_itens[('pá', '1107094')] = ['bbg_carcaca', 'bbg_dianteiro', 'bbg_traseiro']
    
    ref_itens[('acém', '1107095')] = ['bbg_carcaca', 'bbg_dianteiro', 'bbg_traseiro']
    
    ref_itens[('peito', '1107096')] = ['bbg_carcaca', 'bbg_dianteiro', 'bbg_traseiro']
    
    ref_itens[('costela', '1107099')] = ['bbg_carcaca', 'bbg_dianteiro', 'bbg_traseiro']
    
    ref_itens[('carne de porco', '1107018')] = ['cepea_suinos_mg', 'cepea_suinos_pr', 'cepea_suinos_rs',
                                                'cepea_suinos_sc', 'cepea_suinos_sp']
    
    ref_itens[('cafe moido', '1114022')] = ['cepea_cafe_robusta_brl', 'cepea_cafe_arabica_brl']
    
    ref_itens[('leite longa vida', '1111004')] = ['cepea_leite_pbruto_go', 'cepea_leite_pbruto_mg', 'cepea_leite_pbruto_rs',
                          'cepea_leite_pbruto_sp', 'cepea_leite_pbruto_pr', 'cepea_leite_pbruto_ba',
                          'cepea_leite_pbruto_sc', 'cepea_leite_pbruto_brasil',
                          'cepea_leite_pliquido_go', 'cepea_leite_pliquido_mg',
                          'cepea_leite_pliquido_rs', 'cepea_leite_pliquido_sp',
                          'cepea_leite_pliquido_pr', 'cepea_leite_pliquido_ba',
                          'cepea_liquido_sc', 'cepea_leite_pliquido_brasil']
    
    ref_itens[('ervilha', '1115006')] = ['ceagesp_ERVILHA_TORTA_EXTRAAA', 'ceagesp_ERVILHA_TORTA_EXTRAA',
                            'ceagesp_ERVILHA_TORTA_EXTRA']
    
    ref_itens[('milho verde', '1115058')] = ['ceagesp_MILHOVERDE__EXTRA',
                            'ceagesp_MILHOVERDE__ESPECIAL', 'ceagesp_MILHOVERDE__PRIMEIRA']
    
    ref_itens[('palmito', '1115016')] = ['ceagesp_PALMITO_PUPUNHA_']
    
    ref_itens[('alho', '1116010')] = ['ceagesp_ALHOESTRANG_CHINES_', 'ceagesp_ALHO__TIPO7',
                               'ceagesp_ALHO__TIPO6', 'ceagesp_ALHO__TIPO5',
                               'prohort_ALHO']
    
    ref_itens[('farinha de mandioca', '1102023')] = ['cepea_mandioca_farinha_fina_avista_som',
                            'cepea_mandioca_farinha_fina_prazo_som',
                            'cepea_mandioca_farinha_fina_prazo_pgto_som',
                            'cepea_mandioca_farinha_fina_avista_cop',
                            'cepea_mandioca_farinha_fina_prazo_cop',
                            'cepea_mandioca_farinha_fina_prazo_pgto_cop',
                            'cepea_mandioca_farinha_fina_avista_eop',
                            'cepea_mandioca_farinha_fina_prazo_eop',
                            'cepea_mandioca_farinha_fina_prazo_pgto_eop',
                            'cepea_mandioca_farinha_fina_avista_nop',
                            'cepea_mandioca_farinha_fina_prazo_nop',
                            'cepea_mandioca_farinha_fina_prazo_pgto_nop',
                            'cepea_mandioca_farinha_fina_avista_aic',
                            'cepea_mandioca_farinha_fina_prazo_aic',
                            'cepea_mandioca_farinha_fina_prazo_pgto_aic',
                            'cepea_mandioca_farinha_fina_avista_lsc',
                            'cepea_mandioca_farinha_fina_prazo_lsc',
                            'cepea_mandioca_farinha_fina_prazo_pgto_lsc',
                            'cepea_mandioca_farinha_fina_avista_ass',
                            'cepea_mandioca_farinha_fina_prazo_ass',
                            'cepea_mandioca_farinha_fina_prazo_pgto_ass',
                            'cepea_mandioca_farinha_grossa_avista_som',
                            'cepea_mandioca_farinha_grossa_prazo_som',
                            'cepea_mandioca_farinha_grossa_prazo_pgto_som',
                            'cepea_mandioca_farinha_grossa_avista_cop',
                            'cepea_mandioca_farinha_grossa_prazo_cop',
                            'cepea_mandioca_farinha_grossa_prazo_pgto_cop',
                            'cepea_mandioca_farinha_grossa_avista_eop',
                            'cepea_mandioca_farinha_grossa_prazo_eop',
                            'cepea_mandioca_farinha_grossa_prazo_pgto_eop',
                            'cepea_mandioca_farinha_grossa_avista_nop',
                            'cepea_mandioca_farinha_grossa_prazo_nop',
                            'cepea_mandioca_farinha_grossa_prazo_pgto_nop',
                            'cepea_mandioca_farinha_grossa_avista_aic',
                            'cepea_mandioca_farinha_grossa_prazo_aic',
                            'cepea_mandioca_farinha_grossa_prazo_pgto_aic',
                            'cepea_mandioca_farinha_grossa_avista_lsc',
                            'cepea_mandioca_farinha_grossa_prazo_lsc',
                            'cepea_mandioca_farinha_grossa_prazo_pgto_lsc',
                            'cepea_mandioca_farinha_grossa_avista_ass',
                            'cepea_mandioca_farinha_grossa_prazo_ass',
                            'cepea_mandioca_farinha_grossa_prazo_pgto_ass',
                            'cepea_mandioca_fecula_avista_esm',
                            'cepea_mandioca_fecula_prazo_esm',
                            'cepea_mandioca_fecula_prazo_pgto_esm',
                            'cepea_mandioca_fecula_avista_som',
                            'cepea_mandioca_fecula_prazo_som',
                            'cepea_mandioca_fecula_prazo_pgto_som',
                            'cepea_mandioca_fecula_avista_cop',
                            'cepea_mandioca_fecula_prazo_cop',
                            'cepea_mandioca_fecula_prazo_pgto_cop',
                            'cepea_mandioca_fecula_avista_eop',
                            'cepea_mandioca_fecula_prazo_eop',
                            'cepea_mandioca_fecula_prazo_pgto_eop',
                            'cepea_mandioca_fecula_avista_nop',
                            'cepea_mandioca_fecula_prazo_nop',
                            'cepea_mandioca_fecula_prazo_pgto_nop',
                            'cepea_mandioca_fecula_avista_sop',
                            'cepea_mandioca_fecula_prazo_sop',
                            'cepea_mandioca_fecula_prazo_pgto_sop',
                            'cepea_mandioca_fecula_avista_aic',
                            'cepea_mandioca_fecula_prazo_aic',
                            'cepea_mandioca_fecula_prazo_pgto_aic',
                            'cepea_mandioca_fecula_avista_lsc',
                            'cepea_mandioca_fecula_prazo_lsc',
                            'cepea_mandioca_fecula_prazo_pgto_lsc',
                            'cepea_mandioca_fecula_avista_ass',
                            'cepea_mandioca_fecula_prazo_ass',
                            'cepea_mandioca_fecula_prazo_pgto_ass',
                            'cepea_mandioca_raiz_avista_esm',
                            'cepea_mandioca_raiz_prazo_esm',
                            'cepea_mandioca_raiz_prazo_pgto_esm',
                            'cepea_mandioca_raiz_avista_som',
                            'cepea_mandioca_raiz_prazo_som',
                            'cepea_mandioca_raiz_prazo_pgto_som',
                            'cepea_mandioca_raiz_avista_cop',
                            'cepea_mandioca_raiz_prazo_cop',
                            'cepea_mandioca_raiz_prazo_pgto_cop',
                            'cepea_mandioca_raiz_avista_eop',
                            'cepea_mandioca_raiz_prazo_eop',
                            'cepea_mandioca_raiz_prazo_pgto_eop',
                            'cepea_mandioca_raiz_avista_nop',
                            'cepea_mandioca_raiz_prazo_nop',
                            'cepea_mandioca_raiz_prazo_pgto_nop',
                            'cepea_mandioca_raiz_avista_aic',
                            'cepea_mandioca_raiz_prazo_aic',
                            'cepea_mandioca_raiz_prazo_pgto_aic',
                            'cepea_mandioca_raiz_avista_lsc',
                            'cepea_mandioca_raiz_prazo_lsc',
                            'cepea_mandioca_raiz_prazo_pgto_lsc',
                            'cepea_mandioca_raiz_avista_ass',
                            'cepea_mandioca_raiz_prazo_ass',
                            'cepea_mandioca_raiz_prazo_pgto_ass']
    
    return ref_itens


def list_itens(ref):
    """Cria uma lista com o agregado dos produtos a partir de cada item do grupo de referência
    (em ref vai o número do grupo). Dropa itens duplicados."""
    
    ref_itens = make_ref()

    out_list = []

    for ituple in ref_itens:
        if ituple[1][:4] == ref:
            out_list += ref_itens[ituple]
    
    out_list = list(set(out_list))
    
    return out_list


#def from_prohort(sheet):
#    db = shelve.open(r'F:\DADOS\ASSET\MACROECONOMIA\DADOS\Inflação\9.PROHORT\items_prohort')
#    
#    items_prohort = db['items_prohort']
#    
#    out_list = []
#    for el in items_prohort:
#        if 'prohort_'+sheet in el:
#            out_list.append(el)
#    
#    return out_list


def prohort_pond():
    # já estão com a nova POF
    ipca_pond = {}
    ipca_pond['AC'] = 0.51
    ipca_pond['PA'] = 3.91
    ipca_pond['MA'] = 1.62
    ipca_pond['CE'] = 3.22
    ipca_pond['PE'] = 3.93
    ipca_pond['SE'] = 1.02
    ipca_pond['BA'] = 5.99
    ipca_pond['BH'] = 9.74
    ipca_pond['ES'] = 1.86
    ipca_pond['RJ'] = 9.41
    ipca_pond['SP'] = 32.32
    ipca_pond['PR'] = 8.05
    ipca_pond['RS'] = 8.59
    ipca_pond['MS'] = 1.58
    ipca_pond['GO'] = 4.16
    ipca_pond['DF'] = 4.09
    
    ref_prohort = {}
    ref_prohort['SP'] = ['CEAGESP - Bauru', 'CEAGESP - Franca', 'CEAGESP - Piracicaba',
                         'CEAGESP - Ribeirão Preto', 'CEAGESP - São José do Rio Preto',
                         'CEAGESP - São José dos Campos', 'CEAGESP - São Paulo',
                         'CEAGESP - Sorocaba', 'CEAGESP - Araraquara', 'CEAGESP - Araçatuba',
                         'CEASA-SP - Campinas', 'CEAGESP - Presidente Prudente', 'CEAGESP - Marília',
                         'CEASA-SP - Santo André (CRAISA)']
    ref_prohort['BA'] = ['CEASA-BA - Salvador ( EBAL )', 'CEASA-BA - Paulo Afonso']
    ref_prohort['DF'] = ['CEASA-DF - Brasília']
    ref_prohort['ES'] = ['CEASA-ES - Vitória']
    ref_prohort['GO'] = ['CEASA-GO - Goiania']
    ref_prohort['MG'] = ['CEASA-MG - Grande BH', 'CEASA-MG - Uberaba', 'CEASA-MG - Juiz de Fora',
                         'CEASA-MG -Barbacena', 'CEASA-MG - Uberlândia', 'CEASA-MG - Caratinga',
                         'CEASA-MG - Governador Valadares']
    ref_prohort['PB'] = ['CEASA-PB - Campina Grande ( EMPASA )', 'CEASA-PB - João Pessoa ( EMPASA )']
    ref_prohort['PE'] = ['CEASA-PE - Recife', 'CEASA-PE - Caruaru']
    ref_prohort['RJ'] = ['CEASA-RJ - Rio de Janeiro']
    ref_prohort['RS'] = ['CEASA-RS - Porto Alegre', 'CEASA-RS - Caxias do Sul']
    ref_prohort['BA'] = ['CEASA-BA - Juazeiro ( Mercado do Produtor )']
    ref_prohort['CE'] = ['CEASA-CE - Fortaleza', 'CEASA-CE - Cariri', 'CEASA-CE - TIANGUÁ',
                         'CEASA-CE - Ibiapaba']
    ref_prohort['MA'] = ['CEASA-MA- São Luiz (COOP. DOS HORTIGRANJEIROS DO MA)']
    ref_prohort['PR'] = ['CEASA-PR - Curitiba', 'CEASA-PR - Maringá', 'CEASA-PR - Londrina',
                         'CEASA-PR - Foz do Iguaçu']
    ref_prohort['SE'] = ['CEASA-SE - Aracaju']
    ref_prohort['PA'] = ['CEASA-PA - Belem']
    ref_prohort['MS'] = ['CEASA-MS - Campo Grande']
    ref_prohort['AC'] = ['CEASA-AC - Rio Branco']
    
    return ref_prohort, ipca_pond
    

























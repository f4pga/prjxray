LVCMOS       = ['LVCMOS12', 'LVCMOS15', 'LVCMOS18']

# TODO: add support for digitally controlled impedance (_DCI) and termination (_T)
SSTL         = ['SSTL15',  #'SSTL15_DCI',  'SSTL15_T_DCI'
                'SSTL135', #'SSTL135_DCI', 'SSTL135_T_DCI'
                'SSTL12',  #'SSTL12_DCI',  'SSTL12_T_DCI'
               ]

# TODO: add support for digitally controlled impedance (_DCI) and termination (_T)
DIFF_SSTL15  = ['DIFF_SSTL15',  ] # 'DIFF_SSTL15_DCI',  'DIFF_SSTL15_T_DCI']
DIFF_SSTL135 = ['DIFF_SSTL135', ] # 'DIFF_SSTL135_DCI', 'DIFF_SSTL135_T_DCI']
DIFF_SSTL12  = ['DIFF_SSTL12',  ] # 'DIFF_SSTL12_DCI',  'DIFF_SSTL12_T_DCI']
DIFF_SSTL    = DIFF_SSTL15 + DIFF_SSTL135 + DIFF_SSTL12

LVDS         = ['LVDS']

DIFF         = DIFF_SSTL + LVDS
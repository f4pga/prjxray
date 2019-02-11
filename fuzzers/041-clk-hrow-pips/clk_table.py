HCLKS = 24
GCLKS = 32
SIDE_CLK_INPUTS = 14
CLK_TABLE = {}

CLK_TABLE_NUM_ROWS = 8
CLK_TABLE_NUM_COLS = 8

for gclk in range(GCLKS):
    gclk_name = 'CLK_HROW_R_CK_GCLK{}'.format(gclk)
    row = gclk % CLK_TABLE_NUM_ROWS
    column = int(gclk / CLK_TABLE_NUM_ROWS)
    CLK_TABLE[gclk_name] = (row, column)

for row in range(8):
    CLK_TABLE['CLK_HROW_CK_IN_L{}'.format(row)]  = (row, 4)
for row in range(6):
    CLK_TABLE['CLK_HROW_CK_IN_L{}'.format(row+8)]  = (row, 5)

for row in range(8):
    CLK_TABLE['CLK_HROW_CK_IN_R{}'.format(row)]  = (row, 6)
for row in range(6):
    CLK_TABLE['CLK_HROW_CK_IN_R{}'.format(row+8)]  = (row, 7)

# HROW_CK_INT_<X>_<Y>, Y == Y share the same bits, and only X = 0 or X = 1 are
# present on a particular HROW.
for y in range(2):
    for x in range(2):
        int_clk_name = 'CLK_HROW_CK_INT_{}_{}'.format(x, y)
        CLK_TABLE[int_clk_name] = (y+6, 7)

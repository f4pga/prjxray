import sys


def top_harness(DIN_N, DOUT_N, f=sys.stdout):
    f.write(
        '''
module top(input clk, stb, di, output do);
    localparam integer DIN_N = %d;
    localparam integer DOUT_N = %d;

    reg [DIN_N-1:0] din;
    wire [DOUT_N-1:0] dout;

    reg [DIN_N-1:0] din_shr;
    reg [DOUT_N-1:0] dout_shr;

    always @(posedge clk) begin
        din_shr <= {din_shr, di};
        dout_shr <= {dout_shr, din_shr[DIN_N-1]};
        if (stb) begin
            din <= din_shr;
            dout_shr <= dout;
        end
    end

    assign do = dout_shr[DOUT_N-1];

    roi roi (
        .clk(clk),
        .din(din),
        .dout(dout)
    );
endmodule
''' % (DIN_N, DOUT_N))


def instance(mod, name, ports, params={}, sort=True):
    # TODO: make this print nicer
    tosort = sorted if sort else lambda x: x
    print('    %s' % mod)
    if len(params):
        print('        #(')
        for i, (paramk, paramv) in enumerate(tosort(params.items())):
            comma = '' if i == len(params) - 1 else ','
            print('            .%s(%s)%s' % (paramk, paramv, comma))
        print('        )')
    print('        %s (' % name)
    for i, (portk, portv) in enumerate(tosort(ports.items())):
        comma = '' if i == len(ports) - 1 else ','
        print('            .%s(%s)%s' % (portk, portv, comma))
    print('        );')


def quote(s):
    return '"' + s + '"'


def unquote(s):
    assert s[0] == '"' and s[-1] == '"'
    return s[1:-1]


def parsei(s):
    if s == "1'b0":
        return 0
    elif s == "1'b1":
        return 1
    else:
        assert 0, 'FIXME'

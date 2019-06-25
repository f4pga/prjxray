import sys
import random


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


def instance(mod, name, ports, params={}, sort=True, string_buffer=sys.stdout):
    # TODO: make this print nicer
    tosort = sorted if sort else lambda x: x
    print('    %s' % mod, file=string_buffer)
    if len(params):
        print('        #(', file=string_buffer)
        for i, (paramk, paramv) in enumerate(tosort(params.items())):
            comma = '' if i == len(params) - 1 else ','
            print(
                '            .%s(%s)%s' % (paramk, paramv, comma),
                file=string_buffer)
        print('        )', file=string_buffer)
    print('        %s (' % name, file=string_buffer)
    for i, (portk, portv) in enumerate(tosort(ports.items())):
        comma = '' if i == len(ports) - 1 else ','
        print(
            '            .%s(%s)%s' % (portk, portv, comma),
            file=string_buffer)
    print('        );', file=string_buffer)


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


def parse_bitstr(s):
    n, postfix = s.split("'")
    n = int(n)
    assert postfix[0] == 'b'
    bitstr = postfix[1:]
    assert len(bitstr) == n
    return [int(x) for x in bitstr]


def vrandbit():
    if random.randint(0, 1):
        return "1'b1"
    else:
        return "1'b0"


def vrandbits(n):
    ret = "%u'b" % n
    for _i in range(n):
        ret += str(random.randint(0, 1))
    return ret

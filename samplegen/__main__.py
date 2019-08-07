import os
import sys
import argparse
from scipy.io import wavfile

try:
    import samplegen
except ImportError:
    _here = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.join(_here, ".."))
    import samplegen

class MyParser(argparse.ArgumentParser):
    def print_help(self):
        super().print_help()
        print("")
        print("Note must be in the range 0 <= note <= 127")
        print("""
    C   C#  D   D#  E   F   F#  G   G#  A   A#  B  
-1   0   1   2   3   4   5   6   7   8   9  10  11
 0  12  13  14  15  16  17  18  19  20  21  22  23 
 1  24  25  26  27  28  29  30  31  32  33  34  35 
 2  36  37  38  39  40  41  42  43  44  45  46  47 
 3  48  49  50  51  52  53  54  55  56  57  58  59 
 4  60  61  62  63  64  65  66  67  68  69  70  71 
 5  72  73  74  75  76  77  78  79  80  81  82  83 
 6  84  85  86  87  88  89  90  91  92  93  94  95 
 7  96  97  98  99  100 101 102 103 104 105 106 107
 8  108 109 110 111 112 113 114 115 116 117 118 119
 9  120 121 122 123 124 125 126 127""")

    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)       

def msg(s=""):
    print(s)

def file_overwrite(filename):
    if os.path.isfile(filename):
        response = input("File {:s} exists. Overwrite? y/[n]: ".format(filename))
        if response == "y":
            return True
        else:
            return False
    else:
        return True

def main():
    parser = MyParser()
    parser.add_argument("wavfile", type=str, help="input sample file")
    parser.add_argument("note", type=int, help="midi root note of wavfile")
    parser.add_argument("-l", "--loop", action="store_true", default=True, help="automatically loop the sample")
    parser.add_argument("--bitwig", type=str, default="", help="generate bitwig multisample file")
    args = parser.parse_args()

    if args.note < 0 or 127 < args.note:
        msg("Note number must be in the range (0 <= note <= 127)")
        sys.exit()

    msg("LOOP POINTS:")
    if args.loop:
        fs, x = wavfile.read(args.wavfile)
        l1, l2, R = samplegen.loop.find_loop_points(x)
        msg("Found {:d} and {:d} (correlation: {:.1f} %".format(l1, l2, 100*R))
    else:
        msg("Skipped...")
        l1, l2 = 0, 0
    msg()

    msg("OUTPUT:")
    if args.bitwig != "":
        msg("Saving Bitwig multisample")
        if file_overwrite(args.bitwig):
            samplegen.bitwig.write_single(
                args.bitwig,
                samplegen.sample_t(
                    filename = args.wavfile,
                    note_root = args.note,
                    note_max = 127,
                    note_min = 0,
                    loop_start = l1,
                    loop_stop = l2,
                )
            )

    pass

if __name__ == "__main__":
    main()

import libvhd.vhdutils as vhdutils
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: vhd_check.py <filename.vhd>")
        sys.exit(1)

    filename = sys.argv[1]
    vhdutils.check(filename, check_bitmaps=True, check_parents=True)

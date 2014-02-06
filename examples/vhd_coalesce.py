import libvhd.vhdutils as vhdutils
import sys

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: vhd_coalesce.py <filename.vhd> <output.vhd>")
        sys.exit(1)

    filename = sys.argv[1]
    output = sys.argv[2]
    vhdutils.coalesce(filename, output=output)

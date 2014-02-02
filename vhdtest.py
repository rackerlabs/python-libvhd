import libvhd
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: vhdtest.py <filename.vhd>")
        sys.exit(1)

    filename = sys.argv[1]
    vhd = libvhd.VHD(filename, flags='fast')

    footer = vhd.get_footer()

    print("Footer: %s" % str(footer))

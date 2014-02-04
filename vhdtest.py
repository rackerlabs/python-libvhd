import libvhd.libvhd as libvhd
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: vhdtest.py <filename.vhd>")
        sys.exit(1)

    filename = sys.argv[1]
    vhd = libvhd.VHD(filename)

    footer = vhd.get_footer()
    print("Footer: %s\n" % str(footer))

    header = vhd.get_header()
    print("Header: %s\n" % str(header))

    max_virtual_size = vhd.get_max_virtual_size()
    print("Max virtual size: %d" % max_virtual_size)

    chain_depth = vhd.get_chain_depth()
    print("Chain depth: %d" % chain_depth)

    vhd.close()
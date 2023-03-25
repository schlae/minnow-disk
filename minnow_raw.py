import sys

if len(sys.argv) != 2:
    print("Usage: minnow.py datafile.csv")
    quit()

pll_filter_coeff = 0.05

f = open(sys.argv[1], 'r')
dummy = f.readline()
d = f.readlines()
f.close

# Ingest the CSV
parsed = []
for line in d:
    vv = line.strip().split(',')
    (t, db, idx) = vv[0:3]
    #(t, db, idx) = line.strip().split(',')
    parsed.append([float(t), int(db), int(idx)])

print("Finished parsing input data file.")

# Process the FM data
sectorpulse = 0
t_old = parsed[0][0]
bitcell = 8.2e-6 # Will get averaged out
rawdat = []
sp = 0
for [t, d, idx] in parsed:
    # Look for sector pulse falling edge
    if sectorpulse == 0 and idx == 1:
        sectorpulse = 1
    if sectorpulse == 1 and idx == 0:
        sectorpulse = 0
        rawdat.append("x")
        sp += 1
    # Look for positive pulses, ignore all data during sector pulse
    if d == 1:
        delta_t = t - t_old
        t_old = t

        # Now classify this as a 1 or a 0
        if (delta_t > 0.75 * bitcell):
            rawdat.append("L")
            bitcell = ((1 - pll_filter_coeff) * bitcell) + (pll_filter_coeff * delta_t)
        else:
            rawdat.append("S")
            bitcell = ((1 - pll_filter_coeff) * bitcell) + (pll_filter_coeff * delta_t * 2)

# OK, this disk seems to be turning the opposite direction. So let's flip all the bits around before continuing.
rawdat.reverse()

# Turn into string
rawdat = ''.join(rawdat)

#print (rawdat)
#quit()

print("Parsing")


def ToNum(value):
    v = 0
    for i in range(8):
        v |= int(value[i + 1]) << (7 - i)
    return v

#print(hex(ToNum("1000100011")))
#print(hex(ToNum("1111111100")))

# Now turn into 0 and 1
tdat = ""
hdat = ""
sectordat = ""
i = 0
sfound = 0
bcount = 0
print(len(rawdat))
while i < (len(rawdat) - 3):
    if rawdat[i] == "x":
        tdat += "SECTORPULSE"
        sfound = 1  # Trigger the state machine to look at sector data
        hdat = ""
        i += 1
    elif rawdat[i] == "L":
        tdat += "0"
        hdat += "0"
        i += 1
    elif (rawdat[i] == "S") and (rawdat[i + 1] == "S"):
        tdat += "1"
        hdat += "1"
        i += 2
    elif (rawdat[i] == "S") and (rawdat[i + 1] == "L"):
        tdat += "ENCERR"
        i += 1
    else:
        tdat += "ERR"
        i += 1

    # State machine
    # First state: Found the hardware sector hole, now find the start of the sector
    if (sfound == 1) and (hdat[-17:] == "00000000000000001"):
        # Print sector data from previous sector
        if len(sectordat) > 0:
            print (sectordat)
            sectordat = ""
        hdat = "1"
        tdat += "\n"
        sfound = 2
        bcount = 0
        print("Sector")
    # Second state: Sector is synced up and we have the first full data byte: the sector ID
    elif (sfound == 2) and len(hdat) == 10:
        # Found a byte, parse this byte
        es = ""
        if bcount == 0:
            hdrbyte = ToNum(hdat)
            es = " - Track %d, Sector %d" % (hdrbyte >> 3, hdrbyte & 0x7)
        else:
            es = " %.2X" % (ToNum(hdat))
        print("%d: %s %s" % (bcount, hdat, es))
        bcount += 1
        hdat = ""
        tdat += "\n"
        # sfound = 2 # Print the next byte
        sfound = 3
        sectordat = ""
    # Third state: Sector ID has been printed, just print the rest of the data payload once
    # we hit the start of the next sector.
    elif sfound == 3:
        sectordat += hdat
        hdat = ""
        



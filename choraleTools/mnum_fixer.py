from pathlib import Path

from music21 import *

p = Path('/Users/Cuthbert/Desktop/Norman_Schmidt_Chorales')
pOut = p.parent / 'Out_Chorales'

def run():    
    files = list(p.iterdir())
    filenames = [fp.name for fp in files]
    pos = 0
    for c in corpus.chorales.Iterator():
        cName = c.filePath.name
        if '.krn' in cName:
            continue
        if '.xml' in cName:
            cName = cName.replace('.xml', '.mxl')
        if cName not in filenames:
            print('skipping', cName)
            continue
        pos += 1
        runOne(c, cName)
        
def runOne(c, cName):
    pName = p / cName
    newScore = converter.parse(pName)
    newScore.metadata.composer = 'J.S. Bach'
    allSuffixesByPart = set()
    for part in newScore.parts:
        priorMeasure = None
        priorMeasureWasIncomplete = False
        priorMeasureDuration = 0.0
        measureNumberShift = 0
        partNumSuffix = []

        for m in part.getElementsByClass('Measure'):
            mn = m.number
            ms = m.numberSuffix
            mns = m.measureNumberWithSuffix()
            ts = m.timeSignature or m.getContextByClass('TimeSignature')
            if ts is None:
                print("No time signature context!", cName, part.id, mns)
                continue
            barQl = ts.barDuration.quarterLength
            mQl = m.duration.quarterLength
            short = barQl - mQl
            perfect = True if short == 0 else False
            pickup = True if not perfect and short > (barQl / 2) else False
            truncated = True if not perfect and short < (barQl / 2) else False
            half = True if not perfect and short == (barQl / 2) else False

            if half and priorMeasureWasIncomplete==False:
                priorMeasureWasIncomplete = True
                priorMeasureDuration = mQl
                priorMeasure = m
                m.number = mn - measureNumberShift
                partNumSuffix.append((mn - measureNumberShift, ms))
            elif half and priorMeasureWasIncomplete and priorMeasureDuration == short:
                priorMeasureWasIncomplete = False
                m.paddingLeft = short
                priorMeasure = m
                priorMeasureDuration = mQl
                measureNumberShift += 1
                if ms is None:
                    ms = 'a'
                else:
                    ms = ms + 'a'
                m.number = mn - measureNumberShift
                m.numberSuffix = ms
                partNumSuffix.append((mn - measureNumberShift, ms))
                
            elif perfect:
                priorMeasureWasIncomplete = False
                priorMeasureDuration = mQl
                priorMeasure = m
                m.number = mn - measureNumberShift
                partNumSuffix.append((mn - measureNumberShift, ms))
            elif pickup and priorMeasure is None:
                # pickup measure 1
                partNumSuffix.append((0, ms))
                m.number = 0
                measureNumberShift += 1
            elif truncated and priorMeasureWasIncomplete and priorMeasureDuration == short:
                print("Truncated measure following pickup...", cName, part.id, mn)
                priorMeasure.paddingRight = priorMeasure.paddingLeft
                priorMeasure.paddingLeft = 0
                measureNumberShift += 1
                priorMeasure = m
                priorMeasureDuration = mQl
                if ms is None:
                    ms = 'x'
                else:
                    ms = ms + 'x'
                m.number = mn - measureNumberShift
                m.numberSuffix = ms
                partNumSuffix.append((mn - measureNumberShift, ms))                
            elif truncated:
                priorMeasureWasIncomplete = True
                m.paddingRight = short
                priorMeasure = m
                priorMeasureDuration = mQl
                m.number = mn - measureNumberShift
                partNumSuffix.append((mn - measureNumberShift, ms))
            elif pickup and not priorMeasureWasIncomplete:
                print("Pickup following complete prior measure", cName, part.id, mn)
                priorMeasureWasIncomplete = True
                m.paddingLeft = short
                priorMeasure = m
                priorMeasureDuration = mQl
                m.number = mn - measureNumberShift
                partNumSuffix.append((mn - measureNumberShift, ms))
            elif pickup and priorMeasureWasIncomplete and priorMeasureDuration == short:
                # good, matched up!
                priorMeasureWasIncomplete = True
                m.paddingLeft = short
                priorMeasure = m
                priorMeasureDuration = mQl
                measureNumberShift += 1
                if ms is None:
                    ms = 'a'
                else:
                    ms = ms + 'a'
                m.number = mn - measureNumberShift
                m.numberSuffix = ms
                partNumSuffix.append((mn - measureNumberShift, ms))
            elif pickup and priorMeasureWasIncomplete and ts is not priorMeasure.timeSignature:
                print("Changing TS Pickup", cName, part.id, mn)
                priorMeasureWasIncomplete = True
                m.paddingLeft = short
                priorMeasure = m
                priorMeasureDuration = mQl
                measureNumberShift += 1
                m.number = mn - measureNumberShift
                partNumSuffix.append((mn - measureNumberShift, ms))
        
        partSuffixesTuple = tuple(partNumSuffix)
        allSuffixesByPart.add(partSuffixesTuple)
        
        
    if len(allSuffixesByPart) != 1:
        print("Multiple conflicting measures!", cName)
        print(cName, allSuffixesByPart)

    try:
        kOrig = c.recurse().getElementsByClass('KeySignature')[0]
        kNew = newScore.recurse().getElementsByClass('KeySignature')[0]
        sKOrig = str(kOrig)
        sKNew = str(kNew)
        if kOrig.sharps != kNew.sharps:
            print("Key changed from", kOrig, kNew)
        
        if sKNew != sKOrig:
            kNew.activeSite.replace(kNew, kOrig)
            analysisKey = newScore.analyze('key')
            print('Mode would have been changed from ', sKOrig, sKNew)
            if str(analysisKey) != sKOrig:
                print("Key mismatch: ", sKOrig, sKNew, str(analysisKey))
            
    except IndexError:
        print('no key in ', cName)

    fNewXml = pOut / (cName.replace('.mxl', '.xml'))
    newScore.write(fp=fNewXml)
    musicxml.archiveTools.compressXML(str(fNewXml), deleteOriginal=True)

#     for i, pOrig in enumerate(c.parts):
#         expander = repeat.Expander(pOrig)
#         if not expander.isExpandable():
#             #print('incoherent repeats', cName)
#             try:
#                 pOrig = expander.process()       
#             except Exception:
#                 pass
# 
#         pNew = newScore.parts[i]
#         expander = repeat.Expander(pNew)
#         if not expander.isExpandable():
#             #print('incoherent repeats', cName)
#             try:
#                 pNew = expander.process()
#             except Exception:
#                 pass
# 
#         origPitches = tuple([p.nameWithOctave for p in pOrig.pitches])
#         newPitches = tuple([p.nameWithOctave for p in pNew.pitches])
#         if origPitches != newPitches:
#             print(cName, pOrig.id, len(origPitches), len(newPitches))
#             pNew.show()
#             for i, thisP in enumerate(origPitches):
#                 try:
#                     newP = newPitches[i]
#                 except IndexError:
#                     continue
#                 if thisP != newP:
#                     print(i, thisP, newP)
            

if __name__ == '__main__':
    run()

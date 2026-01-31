import json
import os
import shutil
import subprocess
from typing import List
from fontTools.merge import Merger, Options
from fontTools.ttLib import TTFont
from gftools.fix import rename_font

tiers = json.load(open('../fontrepos.json'))
state = json.load(open('../state.json'))

weightsAndFallbackWeights = [
    ("Thin", ["ExtraLight", "Light", "Regular"]),
    ("ExtraLight", ["Light", "Thin", "Regular"]),
    ("Light", ["Regular"]),
    ("Regular", []),
    ("Medium", ["Regular", "SemiBold"]),
    ("SemiBold", ["Bold", "Regular"]),
    ("Bold", ["ExtraBold", "SemiBold", "Black", "Regular"]),
    ("ExtraBold", ["Black", "Bold", "SemiBold", "Regular"]),
    ("Black", ["ExtraBold", "Bold", "SemiBold", "Regular"]),
]

def findUnprocessedNotoFonts(weight, fallbackWeights) -> List[str]:
    """Returns a list of Noto fonts matching the given weight (or a fallback weight)"""
    banned = ["devanagari", "duployan", "georgian", "latin-greek-cyrillic", "sign-writing", "symbols", "test"]
    selected_repos = [k for k, v in tiers.items() if v.get("tier", 4) <= 3]
    selected_repos = [k for k in selected_repos if k not in banned]
    selected_repos = sorted(selected_repos, key=lambda k: tiers[k]["tier"])
    selected_fonts = []
    for repo in selected_repos:
        if "families" not in state[repo]:
            print(f"Skipping odd repo {repo} (no families)")
            continue
        selected_families = [x for x in state[repo]["families"].keys() if "Sans" in x and "UI" not in x]
        if not selected_families:
            continue
        all_files = state[repo]["families"][selected_families[0]]["files"]
        target = None
        for weight in [weight, *fallbackWeights]:
            files = [ x for x in all_files if f"{weight}.ttf" in x and "UI" not in x and "Condensed" not in x]
            for file in files:
                if "/hinted/" in file:
                    target = file
                    break
            if target is None:
                for file in files:
                    if "/unhinted/" in file:
                        target = file
                        break
            if target is not None:
                break
        if target is None:
            print(f"Couldn't find a target for {repo}")
            continue
        selected_fonts.append("../"+target)
    return selected_fonts

def megamerge(newname, mergeList):
    print("Merging: ")
    for x in mergeList:
        print("  "+os.path.basename(x))

    merger = Merger(options=Options(drop_tables=["vmtx", "vhea", "MATH", "GSUB"]))
    merged = merger.merge(mergeList)
    rename_font(merged, newname)

    # Preserve some tables from Inter
    inter = TTFont(mergeList[0])
    merged["hhea"] = inter["hhea"]
    merged["OS/2"] = inter["OS/2"]

    merged.save(newname.replace(" ","")+".ttf")

def resizeInterFonts():
    """Convert Inter to 1000 UPM to make it compatible with Noto"""
    os.makedirs("tmp/Inter", exist_ok=True)
    for weight, _ in weightsAndFallbackWeights:
        subprocess.Popen(f'''fontforge -lang=ff -c \'
Open("../fonts/Inter/Inter_24pt-{weight}.ttf");
ScaleToEm(1000);
Generate("./tmp/Inter/Inter-UPM1000-{weight}.ttf");
\'''', shell=True).wait()

def getMergeLists():
    """
    Returns a list like this: [
        ("Thin", ["path/to/Inter-Thin.ttf", "path/to/NotoSansAdlam-Thin.ttf"]),
        ...
    ]
    """
    mergeLists: List[(str, List[str])] = []
    for weight, fallbackWeights in weightsAndFallbackWeights:
        mergeList: List[str] = [f"tmp/Inter/Inter-UPM1000-{weight}.ttf"]
        unprocessed_fonts = findUnprocessedNotoFonts(weight, fallbackWeights)
        for unprocessed_font in unprocessed_fonts:
            processed_font = unprocessed_font.replace("../fonts/", "tmp/")
            mergeList.append(processed_font)
            os.makedirs(os.path.dirname(processed_font), exist_ok=True)
            if os.path.isfile(processed_font):
                continue
            # TODO: Process font if needed
            # For now, just copy the font.
            shutil.copy(unprocessed_font, processed_font)
        mergeLists.append((weight, mergeList))
    return mergeLists

if __name__ == "__main__":
    resizeInterFonts()
    mergeLists = getMergeLists()

    for (weight, mergeList) in mergeLists:
        megamerge(f"Inter Noto Sans Hybrid - {weight}", mergeList)

    print("Done")

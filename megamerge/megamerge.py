import json
import os
import subprocess
from fontTools.ttLib import TTFont
from fontTools.merge import Merger, Options
from gftools.fix import rename_font

tiers = json.load(open('../fontrepos.json'))
state = json.load(open('../state.json'))
warnings = []

def megamerge(newname, base_font, tier_predicate, banned, modulation, weight, fallbackWeights):
    glyph_count = len(TTFont(base_font).getGlyphOrder())
    selected_repos = [k for k, v in tiers.items() if tier_predicate(v.get("tier", 4))]
    selected_repos = [k for k in selected_repos if k not in banned]
    selected_repos = sorted(selected_repos, key=lambda k: tiers[k]["tier"])
    mergelist = [base_font]
    for repo in selected_repos:
        if "families" not in state[repo]:
            print(f"Skipping odd repo {repo} (no families)")
            continue
        selected_families = [x for x in state[repo]["families"].keys() if modulation in x and "UI" not in x]
        if not selected_families:
            continue
        all_files = state[repo]["families"][selected_families[0]]["files"]
        target = None
        for weight in [weight, *fallbackWeights]:
            files = [ x for x in all_files if f"{weight}.ttf" in x and "UI" not in x]
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
        target_font = TTFont("../"+target)
        glyph_count += len(target_font.getGlyphOrder())
        if glyph_count > 65535:
            warnings.append(f"Too many glyphs while building {newname}, stopped at {repo}")
            break
        mergelist.append("../"+target)
    print("Merging: ")
    for x in mergelist:
        print("  "+os.path.basename(x))
    merger = Merger(options=Options(drop_tables=["vmtx", "vhea", "MATH"]))
    merged = merger.merge(mergelist)
    rename_font(merged, newname)
    merged.save(newname.replace(" ","")+".ttf")

weightsAndFallbacks = [
    ("Thin", ["ExtraLight", "Light", "Regular"]),
    ("ExtraLight", ["Light", "Regular"]),
    ("Light", ["Regular"]),
    ("Regular", []),
    ("Medium", ["Regular", "SemiBold"]),
    ("SemiBold", ["Bold", "Regular"]),
    ("Bold", ["ExtraBold", "SemiBold", "Black", "Regular"]),
    ("ExtraBold", ["Black", "Bold", "SemiBold", "Regular"]),
    ("Black", ["ExtraBold", "Bold", "SemiBold", "Regular"]),
]

# Convert Inter to 1000 UPM
for weight, fallbackWeights in weightsAndFallbacks:
    subprocess.Popen(f'fontforge -lang=ff -c \' Open("../fonts/Inter/Inter_24pt-{weight}.ttf"); ScaleToEm(1000); Generate("../fonts/Inter/Inter-UPM1000-{weight}.ttf"); \'', shell=True).wait()

for modulation in ["Sans"]:
    banned = ["duployan", "latin-greek-cyrillic", "sign-writing", "test"]
    if modulation == "sans":
        banned.append("devanagari")  # Already included

    for weight, fallbackWeights in weightsAndFallbacks:
        megamerge(f"Inter Noto {modulation} Hybrid - {weight}",
                base_font=f"../fonts/Inter/Inter-UPM1000-{weight}.ttf",
                tier_predicate= lambda x: x <= 3,
                banned=banned,
                modulation=modulation,
                weight=weight,
                fallbackWeights=fallbackWeights,
                )

if warnings:
    print("\n\nWARNINGS:")
    for w in warnings:
        print(w)
else:
    print("Completed successfully")
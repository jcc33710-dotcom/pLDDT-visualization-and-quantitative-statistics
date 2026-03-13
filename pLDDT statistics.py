#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from pathlib import Path
from Bio.PDB import MMCIFParser, PDBParser
from Bio.PDB.NeighborSearch import NeighborSearch

# =========================
# 参数区（只改这里）
# =========================
STRUCTURE_DIR = Path("")
ANNOTATION_FILE = Path("")
OUTPUT_DIR = Path("")
INTERFACE_CUTOFF = 4.0  # Å

OUTPUT_DIR.mkdir(exist_ok=True)

# =========================
# 工具函数
# =========================
def load_structure(path):
    if path.suffix == ".cif":
        parser = MMCIFParser(QUIET=True)
    else:
        parser = PDBParser(QUIET=True)
    return parser.get_structure(path.stem, str(path))


def residue_plddt(residue):
    vals = [atom.get_bfactor() for atom in residue if atom.get_bfactor() is not None]
    return np.mean(vals) if vals else np.nan


# =========================
# 主程序
# =========================
def main():

    anno = pd.read_csv(ANNOTATION_FILE)
    records = []

    for _, row in anno.iterrows():

        model_id = row["model_id"]
        system = row["system"]
        pep_id = row["chain_peptide"]
        rec1_id = row["chain_receptor1"]
        rec2_id = row["chain_receptor2"]

        files = list(STRUCTURE_DIR.glob(f"{model_id}*.cif")) + \
                list(STRUCTURE_DIR.glob(f"{model_id}*.pdb"))

        if not files:
            print(f"[WARN] structure not found: {model_id}")
            continue

        structure = load_structure(files[0])
        model = next(structure.get_models())

        pep_chain = model[pep_id]
        rec_chains = [model[rec1_id], model[rec2_id]]

        # -------- 肽 pLDDT --------
        pep_res = [r for r in pep_chain if r.id[0] == " "]
        pep_plddt = np.mean([residue_plddt(r) for r in pep_res])

        pep_atoms = [a for r in pep_res for a in r]
        ns = NeighborSearch(pep_atoms)

        interface_res = set()
        all_rec_res = []

        for chain in rec_chains:
            for r in chain:
                if r.id[0] != " ":
                    continue
                all_rec_res.append(r)
                for atom in r:
                    if ns.search(atom.coord, INTERFACE_CUTOFF):
                        interface_res.add(r)
                        break

        iface_plddt = np.mean([residue_plddt(r) for r in interface_res])

        non_iface_res = [r for r in all_rec_res if r not in interface_res]
        bg_plddt = np.mean([residue_plddt(r) for r in non_iface_res])

        records.append({
            "model_id": model_id,
            "system": system,
            "peptide_plddt": pep_plddt,
            "interface_plddt": iface_plddt,
            "background_plddt": bg_plddt,
            "n_interface_res": len(interface_res)
        })

    df = pd.DataFrame(records)
    out = OUTPUT_DIR / "plddt_statistics.csv"
    df.to_csv(out, index=False)
    print(f"[OK] results written to {out}")


if __name__ == "__main__":
    main()
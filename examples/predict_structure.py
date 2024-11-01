from pathlib import Path

import numpy as np
import torch

from chai_lab.chai1 import run_inference

# We use fasta-like format for inputs.
# - each entity encodes protein, ligand, RNA or DNA
# - each entity is labeled with unique name;
# - ligands are encoded with SMILES; modified residues encoded like AAA(SEP)AAA

# Example given below, just modify it


example_fasta = """
>protein|evgs-1
MKFLPYIFLLCCGLWSTISFADEDYIEYRGISSNNRVTLDPLRLSNKELRWLASKKNLVIAVHKSQTATL
LHTDSQQRVRGINADYLNLLKRALNIKLTLREYADHQKAMDALAEGEVDIVLSHLVTSPPLNNDIAATKP
LIITFPALVTTLHDSMRPLTSPKPVNIARVANYPPDEVIHQSFPKATIISFTNLYQALASVSAGHNDYFI
GSNIITSSMISRYFTHSLNVVKYYNSPRQYNFFLTRKESVILNEVLNRFVDALTNEVRYEVSQNWLDTGN
LAFLNKPLELTEHEKQWIKQHPNLKVLENPYSPPYSMTDENGSVRGVMGDILNIITLQTGLNFSPITVSH
NIHAGTQLSPGGWDIIPGAIYSEDRENNVLFAEAFITTPYVFVMQKAPDSEQTLKKGMKVAIPYYYELHS
QLKEMYPEVEWIQVDNASAAFHKVKEGELDALVATQLNSRYMIDHYYPNELYHFLIPGVPNASLSFAFPR
GEPELKDIINKALNAIPPSEVLRLTEKWIKMPNVTIDTWDLYSEQFYIVTTLSVLLVGSSLLWGFYLLRS
VRRRKVIQGDLENQISFRKALSDSLPNPTYVVNWQGNVISHNSAFEHYFTADYYKNAMLPLENSDSPFKD
VFSNAHEVTAETKENRTIYTQVFEIDNGIEKRCINHWHTLCNLPASDNAVYICGWQDITETRDLINALEV
EKNKAIKATVAKSQFLATMSHEIRTPISSIMGFLELLSGSGLSKEQRVEAISLAYATGQSLLGLIGEILD
VDKIESGNYQLQPQWVDIPTLVQNTCHSFGAIAASKSIALSCSSTFPEHYLVKIDPQAFKQVLSNLLSNA
LKFTTEGAVKITTSLGHIDDNHAVIKMTIMDSGSGLSQEEQQQLFKRYSQTSAGRQQTGSGLGLMICKEL
IKNMQGDLSLESHPGIGTTFTITIPVEISQQVATVEAKAEQPITLPEKLSILIADDHPTNRLLLKRQLNL
LGYDVDEATDGVQALHKVSMQHYDLLITDVNMPNMDGFELTRKLREQNSSLPIWGLTANAQANEREKGLS
CGMNLCLFKPLTLDVLKTHLSQLHQVAHIAPQYRHLDIEALKNNTANDLQLMQEILMTFQHETHKDLPAA
FQALEAGDNRTFHQCIHRIHGAANILNLQKLINISHQLEITPVSDDSKPEILQLLNSVKEHIAELDQEIA
VFCQKND
>protein|name=evgS-2
MKFLPYIFLLCCGLWSTISFADEDYIEYRGISSNNRVTLDPLRLSNKELRWLASKKNLVIAVHKSQTATL
LHTDSQQRVRGINADYLNLLKRALNIKLTLREYADHQKAMDALAEGEVDIVLSHLVTSPPLNNDIAATKP
LIITFPALVTTLHDSMRPLTSPKPVNIARVANYPPDEVIHQSFPKATIISFTNLYQALASVSAGHNDYFI
GSNIITSSMISRYFTHSLNVVKYYNSPRQYNFFLTRKESVILNEVLNRFVDALTNEVRYEVSQNWLDTGN
LAFLNKPLELTEHEKQWIKQHPNLKVLENPYSPPYSMTDENGSVRGVMGDILNIITLQTGLNFSPITVSH
NIHAGTQLSPGGWDIIPGAIYSEDRENNVLFAEAFITTPYVFVMQKAPDSEQTLKKGMKVAIPYYYELHS
QLKEMYPEVEWIQVDNASAAFHKVKEGELDALVATQLNSRYMIDHYYPNELYHFLIPGVPNASLSFAFPR
GEPELKDIINKALNAIPPSEVLRLTEKWIKMPNVTIDTWDLYSEQFYIVTTLSVLLVGSSLLWGFYLLRS
VRRRKVIQGDLENQISFRKALSDSLPNPTYVVNWQGNVISHNSAFEHYFTADYYKNAMLPLENSDSPFKD
VFSNAHEVTAETKENRTIYTQVFEIDNGIEKRCINHWHTLCNLPASDNAVYICGWQDITETRDLINALEV
EKNKAIKATVAKSQFLATMSHEIRTPISSIMGFLELLSGSGLSKEQRVEAISLAYATGQSLLGLIGEILD
VDKIESGNYQLQPQWVDIPTLVQNTCHSFGAIAASKSIALSCSSTFPEHYLVKIDPQAFKQVLSNLLSNA
LKFTTEGAVKITTSLGHIDDNHAVIKMTIMDSGSGLSQEEQQQLFKRYSQTSAGRQQTGSGLGLMICKEL
IKNMQGDLSLESHPGIGTTFTITIPVEISQQVATVEAKAEQPITLPEKLSILIADDHPTNRLLLKRQLNL
LGYDVDEATDGVQALHKVSMQHYDLLITDVNMPNMDGFELTRKLREQNSSLPIWGLTANAQANEREKGLS
CGMNLCLFKPLTLDVLKTHLSQLHQVAHIAPQYRHLDIEALKNNTANDLQLMQEILMTFQHETHKDLPAA
FQALEAGDNRTFHQCIHRIHGAANILNLQKLINISHQLEITPVSDDSKPEILQLLNSVKEHIAELDQEIA
VFCQKND
>ligand|name=Niacin-1
OC(=O)c1cccnc1
>ligand|name=Niacin-2
OC(=O)c1cccnc1
>ligand|name=ATP-1
O=P(O)(O)OP(=O)(O)OP(=O)(O)OC[C@H]3O[C@@H](n2cnc1c(ncnc12)N)[C@H](O)[C@@H]3O
>ligand|name=ATP-2
O=P(O)(O)OP(=O)(O)OP(=O)(O)OC[C@H]3O[C@@H](n2cnc1c(ncnc12)N)[C@H](O)[C@@H]3O
""".strip()

fasta_path = Path("/home/gruenf/chai-lab-long-context/examples/first-long/example.fasta")
fasta_path.write_text(example_fasta)

output_dir = Path("/home/gruenf/chai-lab-long-context/examples/first-long")

candidates = run_inference(
    fasta_file=fasta_path,
    output_dir=output_dir,
    # 'default' setup
    num_trunk_recycles=3,
    num_diffn_timesteps=200,
    seed=42,
    device=torch.device("cuda:0"),
    use_esm_embeddings=True,
)

cif_paths = candidates.cif_paths
scores = [rd.aggregate_score for rd in candidates.ranking_data]


# Load pTM, ipTM, pLDDTs and clash scores for sample 2
scores = np.load(output_dir.joinpath("scores.model_idx_2.npz"))

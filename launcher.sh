


fasta_file="/srv/nfs/ngs-stockage/NGS_Virologie/GISAID/GISAID_FR.fasta"
metadata_file="/srv/nfs/ngs-stockage/NGS_Virologie/GISAID/metadata.tsv"
nbthreads=8


snakemake -s nextstrain.py \
    --cores $nbthreads \
    --config \
        input_sequence=$fasta_file \
        input_metadata=$metadata_file \
        nbthreads=$nbthreads
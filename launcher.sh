


fasta_file="/srv/nfs/ngs-stockage/NGS_Virologie/GISAID/DEL_NEXT/sequences.fasta"
metadata_file="/srv/nfs/ngs-stockage/NGS_Virologie/GISAID/DEL_NEXT/metadata.tsv"
output_json="DEL"
nbthreads=8

#    -R augur_filter \
snakemake -s nextstrain.py \
    --cores $nbthreads \
    --config \
        input_sequence=$fasta_file \
        input_metadata=$metadata_file \
        nbthreads=$nbthreads \
        json=$output_json
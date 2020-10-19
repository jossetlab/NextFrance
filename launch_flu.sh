raw_seq="/srv/nfs/ngs-stockage/NGS_Virologie/HadrienR/NEXTFLU/ALLSEQ_withoutspace.fasta"
metadata_rep="/srv/nfs/ngs-stockage/NGS_Virologie/HadrienR/NEXTFLU/"
output_dir="/srv/nfs/ngs-stockage/NGS_Virologie/HadrienR/NEXTFLU/"

snakemake -s nextstrainflu.py -p \
    -R augur_filter \
    --cores 8 \
    --use-conda \
    --config input_seq=$raw_seq \
             input_meta=$metadata_rep \
             output_rep=$output_dir

#auspice view --datasetDir auspice
#!/bin/bash
ROOT=`pwd`
ALY_TOOLS_PATH=/nfs/zli_gpu2/bin/developed_softwares/AlchemConvTools
auto_aly_path=/nfs/export3_25T/Bygroup_FEP_data/RBFE_JOBSUB/auto_bygroup_aly
sides='complex ligand'
system=`echo ${ROOT##*/}`
base_path=`echo ${ROOT%/*}`
echo $system $base_path
####Check if the data is already sampled
for side in $sides;do
    cd $ROOT/openmm_run/$side
    # Find directories matching the patterns and store the results in an array
    directories=(`find . -maxdepth 1 -type d \( -name 'restraints*' -o -name 'electrostatics*' -o -name 'sterics*' \)`)
    # Function to extract the numeric part for sorting
    extract_number() {
        echo "$1" | awk 'match($0, /([0-9]+)$/, a) {print a[1] + 0}'
    }
    sorted_dirs=()
    for dir in "${directories[@]}";do
        basename=$(basename "$dir")
        number=$(extract_number "$basename")
        if [[ $basename == restraints* ]]; then
            sorted_dirs+=(`printf "1~%s~%012d\n" "$basename" "$number"`)
        elif [[ $basename == electrostatics* ]]; then
            sorted_dirs+=(`printf "2~%s~%012d\n" "$basename" "$number"`)
        elif [[ $basename == sterics* ]]; then
            sorted_dirs+=(`printf "3~%s~%012d\n" "$basename" "$number"`)
        fi
    done

    IFS=$'\n' sorted_dirs=($(sort -t"~" -k1,1n -k3,3n <<< "${sorted_dirs[*]}"))
    unset IFS
    # Output the sorted results
    for dir in "${sorted_dirs[@]}"; do
        sorted_single_dir=`echo "$dir" | cut -d~ -f2`
        cd $sorted_single_dir   
        if [ -e alc_final_state.xml ]; then
            echo `pwd` "Alchemical MD finished. Ready for analysis."
            ###Check if the csv files copied to the sample_csv_data directory
            # if [ -e copy_finished ]; then
            #     echo `pwd` "remove copy_finished"
            #     rm copy_finished
            # fi
            cd sample_csv_data
            ###Check if the free_ene.csv exist or not, if not, do the analysis
            if [ -e ./fe_cal_out/free_ene.csv ]; then
                echo `pwd` "remove ./fe_cal_out/free_ene.csv"
                rm ./fe_cal_out/free_ene.csv
            fi
            ###Check if the dG_dl.png exist or not, if not, do the plotting dG_dl.png
            if [ $sorted_single_dir == 'restraints' ]; then
                echo "Will not plot the dGdl for restraints."
            else
                if [ -e ./fe_cal_out/*dG_dl.png ]; then
                    echo `pwd` "remove ./fe_cal_out/*dG_dl.png"
                    rm ./fe_cal_out/*dG_dl.png
                fi
            fi
        else
            echo `pwd` "Alchemical MD not finished. Skip."
        fi
        cd $ROOT/openmm_run/$side
    done
done
cd $ROOT
### Collect the analysis results and generate the final dG
if [ -e every_themoprocess_time.png ];then
    echo "remove every_themoprocess_time.png"
    rm every_themoprocess_time.png
fi
if [ -e $ROOT/${system}_whole_mol_fe_time_serial.png ] && [ -e $ROOT/${system}_ligand_fe_time_serial.png ] && [ -e $ROOT/${system}_complex_fe_time_serial.png ]; then
    echo "remove fe_time_serial.png"
    rm *fe_time_serial.png   
fi
if [ -e $ROOT/${system}_report.pdf ]; then
    echo "remove report.pdf"
    rm *report.pdf
fi
if [ -e $ROOT/aly_finished ]; then
    echo "remove aly_finished"
    rm aly_finished
fi

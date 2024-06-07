#!/bin/bash
if [ -L $0 ]; then
    BASE_DIR=`dirname $(readlink $0)`
else
    BASE_DIR=`dirname $0`
fi
basepath=$(cd $BASE_DIR; pwd)
path_file="$basepath/sys_to_aly.txt"

# 读取文件的每一行并遍历
for path in $(cat "$path_file"); do
    # 进入对应的路径
    cd "$path" || continue
    echo `pwd` 
    # 检查是否存在 aly_finished 文件
    if [ ! -e "aly_finished" ]; then
        # 如果不存在,则执行 single_aly.sh 脚本
        echo "will do aly"
        sh $basepath/single_aly.sh > single_aly.log 2>&1 
    fi
    
    # 返回到原始目录
    cd - 
done

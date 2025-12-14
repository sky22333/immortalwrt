import sys
import struct
import os

def parse_dtb(data, offset):
    try:
        # 检查设备树(FDT)魔数
        header_fmt = '>8I'
        header_size = struct.calcsize(header_fmt)
        (magic, totalsize, off_dt_struct, off_dt_strings, off_mem_rsvmap, 
         version, last_comp_version, boot_cpuid_phys) = struct.unpack(header_fmt, data[offset:offset+header_size])
        
        if magic != 0xd00dfeed:
            return None
            
        print(f"在偏移量 {hex(offset)} 处发现设备树(DTB)头")
        
        # 计算结构块和字符串块的偏移
        struct_offset = offset + off_dt_struct
        strings_offset = offset + off_dt_strings
        
        cursor = struct_offset
        stack = []
        
        token_limit = 20000 # 防止无限循环的安全限制
        tokens_read = 0
        
        while cursor < offset + totalsize and tokens_read < token_limit:
            tokens_read += 1
            # 确保4字节对齐
            if (cursor - struct_offset) % 4 != 0:
                cursor += (4 - ((cursor - struct_offset) % 4))
                
            if cursor >= offset + totalsize:
                break
                
            token = struct.unpack('>I', data[cursor:cursor+4])[0]
            cursor += 4
            
            if token == 1: # 开始节点 (FDT_BEGIN_NODE)
                # 节点名是以空字符结尾的字符串
                name_end = data.find(b'\x00', cursor)
                name = data[cursor:name_end].decode('ascii', errors='replace')
                if not name: name = "/"
                stack.append(name)
                # 再次4字节对齐
                cursor = name_end + 1
                if (cursor - struct_offset) % 4 != 0:
                    cursor += (4 - ((cursor - struct_offset) % 4))
                    
            elif token == 2: # 结束节点 (FDT_END_NODE)
                if stack: stack.pop()
                
            elif token == 3: # 属性 (FDT_PROP)
                len_prop, nameoff = struct.unpack('>2I', data[cursor:cursor+8])
                cursor += 8
                
                prop_val = data[cursor:cursor+len_prop]
                cursor += len_prop
                # 属性值后也需要4字节对齐
                if (cursor - struct_offset) % 4 != 0:
                    cursor += (4 - ((cursor - struct_offset) % 4))
                
                # 获取属性名称
                name_str_start = strings_offset + nameoff
                name_str_end = data.find(b'\x00', name_str_start)
                prop_name = data[name_str_start:name_str_end].decode('ascii')
                
                # 我们只关心 mtd-layout 相关的配置
                is_mtd_layout = "mtd-layout" in stack or (len(stack) > 1 and "mtd-layout" in stack[-2])
                if is_mtd_layout:
                     val_str = prop_val.hex()
                     
                     # 尝试将属性值解码为字符串
                     try:
                         s = prop_val.decode('ascii').rstrip('\x00')
                         if all(c.isprintable() for c in s):
                             val_str = f"'{s}'"
                     except:
                         pass

                     # 检查 mtdparts 属性，这里包含了分区信息
                     if prop_name == "mtdparts" and "ubi" in val_str:
                         print(f"\n[在 {stack[-1]} 中发现 MTD 分区配置]")
                         print(f"  原始配置: {val_str}")
                         
                         # 解析格式: nmbm0:1024k(bl2),...,65536k(ubi)
                         try:
                             parts_str = val_str.strip("'").split(':')[1]
                             parts = parts_str.split(',')
                             
                             offset_calc = 0
                             for part in parts:
                                 # 示例部分: "1024k(bl2)"
                                 size_str = part.split('(')[0]
                                 name = part.split('(')[1].rstrip(')')
                                 
                                 size_k = int(size_str.replace('k', ''))
                                 size_bytes = size_k * 1024
                                 
                                 if name == "ubi":
                                     print(f"  UBI 分区起始偏移: {hex(offset_calc)} ({offset_calc/1024/1024:.2f} MB)")
                                     print(f"  UBI 分区大小:     {hex(size_bytes)} ({size_bytes/1024/1024:.2f} MB)")
                                 
                                 offset_calc += size_bytes
                         except Exception as e:
                             print(f"解析 mtdparts 时出错: {e}")

            elif token == 4: # FDT_NOP (空操作)
                pass
            elif token == 9: # FDT_END (结束)
                break
                
        return True

    except Exception as e:
        print(f"在偏移量 {offset} 处解析 DTB 时出错: {e}")
        return None

def main():
    # 配置要分析的 U-Boot 固件文件路径
    # 你可以在这里指定需要分析的固件文件
    firmware_file = 'fip.img'
    
    if not os.path.exists(firmware_file):
        print(f"错误: 找不到文件 {firmware_file}")
        return

    with open(firmware_file, 'rb') as f:
        content = f.read()

    print(f"正在分析 {firmware_file} (文件大小: {len(content)} 字节)...")
    
    # 搜索 DTB 魔数
    magic = b'\xd0\x0d\xfe\xed'
    offset = 0
    found_dtbs = 0
    
    while True:
        offset = content.find(magic, offset)
        if offset == -1:
            break
            
        # 验证是否像一个头文件
        if offset + 40 < len(content):
            if parse_dtb(content, offset):
                found_dtbs += 1
            
        offset += 4
        
    if found_dtbs == 0:
        print("未在文件中发现设备树(DTB)。")

if __name__ == "__main__":
    main()

# replacer_core.py
import re
import shutil
from datetime import datetime
from pathlib import Path
import difflib
import sys # For difflib output

# --- Constants ---
DEFAULT_BACKUP_SUFFIX = ".bak"
STANDARD_INDENT = "    "

# --- Helper Functions ---
def get_indent_str(line: str) -> str:
    match = re.match(r"^(\s*)", line)
    return match.group(1) if match else ""

def is_comment_or_empty(line: str, lang: str = "python") -> bool:
    stripped_line = line.strip()
    if not stripped_line:
        return True
    # Determine language for comment checking based on common extensions
    if lang == "python" and stripped_line.startswith("#"):
        return True
    if (lang == "html" or lang == "xml") and stripped_line.startswith("<!--") and stripped_line.endswith("-->"): # Basic check
        return True
    if lang in ["javascript", "css", "java", "csharp", "cpp", "go", "rust", "swift", "kotlin"] and \
       (stripped_line.startswith("//") or (stripped_line.startswith("/*") and stripped_line.endswith("*/"))): # Basic check
        return True
    return False

# --- Core Logic Functions ---
def backup_file(target_path: Path):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    backup_path = target_path.with_name(f"{target_path.name}.{timestamp}{DEFAULT_BACKUP_SUFFIX}")
    try:
        shutil.copy2(target_path, backup_path)
        print(f"INFO: Backed up '{target_path}' to '{backup_path}'")
    except Exception as e:
        print(f"WARNING: Could not create backup for {target_path}: {e}")

def find_target_block(file_lines: list[str], identifier: dict, target_file_path_str: str) -> tuple[int, int, str] | None:
    block_type = identifier.get('type')
    start_idx, end_idx = -1, -1
    indent_for_replacement = ""
    
    # Try to infer language from file extension for better comment handling
    file_path_obj = Path(target_file_path_str)
    file_extension = file_path_obj.suffix.lower().lstrip('.') if file_path_obj.suffix else "txt"


    # --- NORMALIZATION STEP for block_type ---
    if block_type == "custom_marker": # If LLM outputs singular
        print(f"INFO: Normalizing block_identifier type from 'custom_marker' to 'custom_markers' for '{target_file_path_str}'.")
        block_type = "custom_markers" # Treat it as plural
    # --- END NORMALIZATION ---


    if block_type == "custom_markers":
        start_marker_re_str = identifier.get('start_marker_regex')
        end_marker_re_str = identifier.get('end_marker_regex')
        if not start_marker_re_str or not end_marker_re_str:
            print(f"ERROR: Custom markers identifier for '{target_file_path_str}' requires 'start_marker_regex' and 'end_marker_regex'.")
            return None
        
        try:
            start_marker_re = re.compile(start_marker_re_str)
            end_marker_re = re.compile(end_marker_re_str)
        except re.error as e:
            print(f"ERROR: Invalid regex for custom markers in '{target_file_path_str}': {e}")
            return None

        inclusive = identifier.get('inclusive_markers', False)
        s_line_num, e_line_num = -1, -1

        for i, line in enumerate(file_lines):
            if s_line_num == -1 and start_marker_re.search(line):
                s_line_num = i
            # Search for end marker only after start marker is found
            elif s_line_num != -1 and e_line_num == -1 and end_marker_re.search(line):
                e_line_num = i
                break # Found both start and end

        if s_line_num != -1 and e_line_num != -1 and e_line_num >= s_line_num:
            start_marker_indent = get_indent_str(file_lines[s_line_num])
            if inclusive:
                start_idx = s_line_num
                end_idx = e_line_num
                # If markers are included, the replacement code's base indent should match the start marker's indent.
                indent_for_replacement = start_marker_indent
            else: # Not inclusive, content between markers
                start_idx = s_line_num + 1
                end_idx = e_line_num - 1
                # If there's actual content between markers, match its indent.
                if start_idx <= end_idx and start_idx < len(file_lines): 
                    indent_for_replacement = get_indent_str(file_lines[start_idx])
                else: # No content between markers (insertion point)
                    # Indent relative to the start marker.
                    # If start marker is not a comment, usually content inside is indented.
                    indent_for_replacement = start_marker_indent
                    if not is_comment_or_empty(file_lines[s_line_num], lang=file_extension):
                         indent_for_replacement += STANDARD_INDENT
            
            # Check for valid range. Allows insertion if start_idx == end_idx + 1 (empty block between non-inclusive markers)
            if start_idx > end_idx + 1:
                 print(f"WARNING: Custom marker range invalid for '{target_file_path_str}'. Start index ({start_idx}) > End index + 1 ({end_idx + 1}).")
                 return None 
            return start_idx, end_idx, indent_for_replacement
        
        print(f"INFO: Custom markers not found or out of order in '{target_file_path_str}'. Start found at {s_line_num}, End found at {e_line_num}.")
        return None

    elif block_type in ["function_name", "class_name"]:
        keyword = "def" if block_type == "function_name" else "class"
        name = identifier.get('name')
        if not name:
            print(f"ERROR: Identifier type '{block_type}' for '{target_file_path_str}' requires a 'name'.")
            return None
            
        definition_line_only = identifier.get('definition_line_only', False)
        # Regex: captures indent, keyword, name, and then looks for ( or :
        pattern_str = rf"^(\s*){keyword}\s+{re.escape(name)}\s*(\(|:)"
        try:
            pattern = re.compile(pattern_str)
        except re.error as e:
            print(f"ERROR: Invalid regex for {block_type} '{name}' in '{target_file_path_str}': {e}")
            return None

        def_line_idx = -1
        def_indent = ""

        for i, line in enumerate(file_lines):
            match = pattern.match(line.lstrip()) # Match after lstrip to find def/class not at file start
            if match:
                # Get original indent from the original line, not lstripped one
                def_indent = get_indent_str(file_lines[i])
                def_line_idx = i
                break

        if def_line_idx == -1:
            print(f"INFO: {block_type.capitalize()} '{name}' not found in '{target_file_path_str}'.")
            return None

        # The replacement code will start at the same indent as the def/class line itself.
        indent_for_replacement = def_indent 

        if definition_line_only:
            return def_line_idx, def_line_idx, indent_for_replacement

        # Find end of block (Python/indentation-sensitive language heuristic)
        # Assumes the language uses indentation for blocks (like Python)
        current_idx = def_line_idx + 1
        end_block_content_idx = def_line_idx # Default to just the def line if no body found

        while current_idx < len(file_lines):
            line = file_lines[current_idx]
            line_indent_str = get_indent_str(line)
            
            # Block ends when indent is less than or equal to definition indent, AND line is not empty/comment
            if len(line_indent_str) <= len(def_indent):
                if not is_comment_or_empty(line, lang=file_extension): # file_extension helps here
                    end_block_content_idx = current_idx - 1
                    break
            end_block_content_idx = current_idx # Include this line as part of the block
            current_idx += 1
        else: 
            # Reached end of file, so block extends to the end
            end_block_content_idx = len(file_lines) - 1
        
        # Ensure end_idx is not before def_line_idx
        if end_block_content_idx < def_line_idx:
             end_block_content_idx = def_line_idx 

        return def_line_idx, end_block_content_idx, indent_for_replacement
    
    print(f"ERROR: Unknown or invalid block_identifier type: '{block_type}' for '{target_file_path_str}'.")
    return None

def apply_indentation(replacement_lines: list[str], base_indent_str: str, handling: str) -> list[str]:
    if handling == "as_is":
        return replacement_lines

    if handling == "match_original_block_start":
        if not replacement_lines:
            return []
        # Determine the intrinsic base indentation of the replacement_code block
        current_replacement_base_indent = ""
        first_content_line_found = False
        for line in replacement_lines:
            if line.strip(): # Found a non-blank line
                current_replacement_base_indent = get_indent_str(line)
                first_content_line_found = True
                break
        
        new_lines = []
        for line in replacement_lines:
            if not first_content_line_found and not line.strip(): # Leading blank lines in replacement
                 new_lines.append(base_indent_str + line) # Indent them like the first content line
                 continue
            if not line.strip(): # Other blank lines, preserve them relative to new base
                new_lines.append(line) # Or new_lines.append(base_indent_str) if they should align
                continue

            # Strip its own base indent if it starts with it
            if line.startswith(current_replacement_base_indent):
                stripped_line = line[len(current_replacement_base_indent):]
            else: # Line doesn't have the common base indent (e.g., misaligned line, or a comment not indented with code)
                  # We should still try to preserve its relative position to the block
                  # This logic might need refinement for complex pre-indented snippets
                stripped_line = line # Keep its original form relative to a zero-indent if its indent is less than base
                
            new_lines.append(base_indent_str + stripped_line)
        return new_lines
    
    print(f"WARNING: Unknown indentation_handling type: {handling}. Returning code as_is.")
    return replacement_lines


def perform_replacement_on_content(
    original_lines: list[str], 
    block_identifier: dict, 
    replacement_code: list[str], 
    indentation_handling: str,
    target_file_path_str: str 
    ) -> list[str] | None:
    """
    Core logic that finds block and constructs new content.
    Returns new list of lines, or None if block not found or error.
    """
    if not original_lines and not block_identifier.get('type'): # Handling for new file creation case
        print(f"INFO: No original lines for '{target_file_path_str}', treating as new file content generation.")
        return apply_indentation(replacement_code, "", indentation_handling) # Apply to empty base indent

    find_result = find_target_block(original_lines, block_identifier, target_file_path_str)

    if find_result is None:
        print(f"INFO: Target block not found in '{target_file_path_str}' using identifier: {block_identifier.get('type')}.")
        return None # Block not found
        
    start_idx, end_idx, indent_to_match = find_result
    
    # Handle insertion case for non-inclusive custom markers where start_idx > end_idx
    # This occurs if markers are adjacent e.g. start_idx = 5, end_idx = 4
    is_insertion = (start_idx == end_idx + 1) and \
                   block_identifier.get('type') == 'custom_markers' and \
                   not block_identifier.get('inclusive_markers', False)

    indented_replacement = apply_indentation(replacement_code, indent_to_match, indentation_handling)
    
    new_content_lines = []
    new_content_lines.extend(original_lines[:start_idx])
    new_content_lines.extend(indented_replacement)
    
    if not is_insertion: 
        # Normal replacement: skip the old lines from end_idx + 1
        # Ensure end_idx is valid for slicing original_lines
        if end_idx + 1 <= len(original_lines):
            new_content_lines.extend(original_lines[end_idx + 1:])
        # If end_idx was the last line, original_lines[end_idx + 1:] is correctly empty
    else: 
        # Insertion: append the rest of the original lines from start_idx (which was the line after start_marker)
        # Since start_idx was where insertion begins, original_lines[start_idx:] are the lines after the insertion point
        if start_idx <= len(original_lines): # start_idx can be len(original_lines) if inserting at EOF
             new_content_lines.extend(original_lines[start_idx:])
    
    return new_content_lines

def show_diff(original_text: str, modified_text: str, file_name: str):
    """Prints a unified diff of the changes."""
    # Ensure inputs are strings
    original_text_str = str(original_text) if original_text is not None else ""
    modified_text_str = str(modified_text) if modified_text is not None else ""

    diff_lines = list(difflib.unified_diff(
        original_text_str.splitlines(keepends=True),
        modified_text_str.splitlines(keepends=True),
        fromfile=f"a/{file_name}",
        tofile=f"b/{file_name}"
    ))
    if not diff_lines and original_text_str.strip() == modified_text_str.strip():
        print("INFO: (No effective changes detected by diff)")
    elif not diff_lines and original_text_str != modified_text_str: # Content changed but diff lib didn't show (e.g. only whitespace)
        print("INFO: Content changed, but diff output is empty (likely whitespace or line ending changes).")
        print("--- Original (first 10 lines) ---")
        for line in original_text_str.splitlines()[:10]: print(line)
        if len(original_text_str.splitlines()) > 10: print("...")
        print("--- Modified (first 10 lines) ---")
        for line in modified_text_str.splitlines()[:10]: print(line)
        if len(modified_text_str.splitlines()) > 10: print("...")
    else:
        sys.stdout.writelines(diff_lines)
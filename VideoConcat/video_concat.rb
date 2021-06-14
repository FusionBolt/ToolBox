fragment_list = []
output = 'output.mp4'

base_path = '/Users/username/Library/Containers/com.tencent.tenvideo/Data/Library/Application Support/Download/video/xxx'
Dir.glob("**/*", base: base_path).each do |file|
  next if File.extname(file) != '.ts' # skip the loop if the file is a directory
  fragment_list << File.join(base_path, file)
end

fragment_list = fragment_list.sort_by { |name|
  base_name = File.basename(name)
  [base_name[/\d+/].to_i, name] }

system("ffmpeg -i \"concat:#{fragment_list.join('|')}\" -acodec copy -vcodec copy -absf aac_adtstoasc #{output}")
require 'faraday'
require 'json'
require 'progress_bar'
require 'rainbow/refinement'
require 'cgi'
require 'open3'
require 'URI'

using Rainbow

class HadGetAllPageError < StandardError
end

class DownloadError < StandardError
  def initialize(msg = nil)
    super
  end
end

def get_one_page(fid, page_no)
  con = Faraday.new("https://api.bilibili.com/") do |builder|
    builder.headers['Cookie'] = ""
    builder.headers['User-Agent'] = ""
  end
  response = con.get("https://api.bilibili.com/x/v3/fav/resource/list?media_id=#{fid}&pn=#{page_no}&ps=20&keyword=&order=mtime&type=0&tid=0&platform=web&jsonp=jsonp")
  json = JSON.parse response.body
  raise HadGetAllPageError.new if json['data']['medias'].nil?
  json['data']['medias'].map{|media| [media['title'], "https://www.bilibili.com/video/#{media['bvid']}"]}
end

def get_favorites_list_from_url(favorite_url)
  fid = CGI::parse(URI.parse(favorite_url).query)['fid'][0]
  get_favorites_list_from_fid(fid) 
end

def get_favorites_list_from_fid(fid)
  video_list = []
  page_no = 1
  loop do
    begin
    video_list.concat(get_one_page(fid, page_no))
    page_no += 1
    rescue HadGetAllPageError
      break
    end
  end
  puts "#{video_list.size} videos were collected".green
  video_list
end

# if not specified -o, filename may be 活动作品+title
# ['title', 'bilibili url']
def download(video)
  system('youtube-dl', video[1], '-o', "#{video[0]}.flv")
end

# fail:[title, fail_info]
def output_fail_info(fail_list)
  fail_list.each do |fail|
    puts "Download #{fail[0]} failed, url:#{fail[1]}".red
  end
end

def download_list(video_list, thread_nums = 4)
  bar = ProgressBar.new(video_list.size)
  fail_list = []
  video_list.each_slice(thread_nums) do |list|
    list.map do |video|
      Thread.new do
        unless download(video)
          fail_list << video
        end
      end
    end.each do |video_thread|
       bar.increment!
       video_thread.join
    end
  end
  if fail_list.empty?
    output_fail_info(fail_list)
  else
    puts "Download successful".green
  end
end
# TODO:名字带/会有问题
# TODO:youtube-dl 输出的时候附带作者信息？
# TODO:如果是多集的视频怎么办
# TODO:自动获取cookie
# TODO:如果解析不是url则视为fid
download_list(get_favorites_list_from_url(''))
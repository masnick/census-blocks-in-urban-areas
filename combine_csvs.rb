files = Dir.entries('data/census/output_with_population')[4..-1]

output = File.open('data/census/blocks_with_population.csv', 'w') do |out|
  out.write "ua_name,ua_id,state,county,tract,block,block_geoid,pop\n"
  files.each do |f|
    puts "Starting #{f}"
    # Skip files with only 1 row (just headers)
    next unless %x{wc -l data/census/output_with_population/#{f}}.split.first.to_i > 1
    csv = File.open("data/census/output_with_population/#{f}", 'r')
    counter = 0
    csv.each_line do |line|
      counter += 1
      next if counter == 1
      out.write line
    end
  end
end

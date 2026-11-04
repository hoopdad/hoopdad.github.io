# Jekyll's theme asset reader ignores exclude; this shell supplies its own assets.
Jekyll::Hooks.register :site, :post_read do |site|
  next unless site.theme&.assets_path

  theme_files = Dir.glob(File.join(site.theme.assets_path, "**", "*"))
    .select { |path| File.file?(path) }
    .map { |path| path.delete_prefix("#{site.theme.root}/") }

  site.pages.reject! do |page|
    theme_files.include?(page.relative_path) &&
      !File.file?(site.in_source_dir(page.relative_path))
  end
  site.static_files.reject! do |file|
    file.path.start_with?("#{site.theme.assets_path}/")
  end
end

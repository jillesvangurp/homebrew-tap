class Ktsearch < Formula
  desc "Swiss-army CLI for Elasticsearch/OpenSearch operations"
  homepage "https://github.com/jillesvangurp/kt-search"
  version "2.8.7"
  license "MIT"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/jillesvangurp/kt-search/releases/download/2.8.7/ktsearch-2.8.7-darwin-arm64.tar.gz"
      sha256 "9d3f97435a8779b459bd6c5cf533c67595790de3f21a71e973776540b9d51a7f"
    else
      url "https://github.com/jillesvangurp/kt-search/releases/download/2.8.7/ktsearch-2.8.7-darwin-x64.tar.gz"
      sha256 "7f19574cdefba799f5f2bc644243c60b728b1e901cc984a81a38c7cf9eaac54a"
    end
  end

  on_linux do
    if Hardware::CPU.intel?
      url "https://github.com/jillesvangurp/kt-search/releases/download/2.8.7/ktsearch-2.8.7-linux-x64.tar.gz"
      sha256 "9c138a93bf70c74aa81f3911dadb271658963b837b5f85c4e3e3ce842fad0880"
    else
      odie "ktsearch currently publishes Homebrew binaries for macOS (arm64, x64) and Linux x64 only"
    end
  end

  def install
    bin.install "ktsearch"
    pkgshare.install "alias-and-completions.sh", "install.sh", "uninstall.sh"

    generate_completions_from_executable(bin/"ktsearch", "completion", shells: [:bash, :zsh])
  end

  test do
    output = shell_output("#{bin}/ktsearch --help")
    assert_match "Swiss-army CLI for Elasticsearch/OpenSearch operations.", output
  end
end

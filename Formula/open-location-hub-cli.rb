class OpenLocationHubCli < Formula
  desc "CLI for Open Location Hub"
  homepage "https://github.com/Open-Location-Stack/open-location-hub-cli"

  # STABLE-BEGIN
  version "0.1.0"
  license "MIT"
  head "https://github.com/Open-Location-Stack/open-location-hub-cli.git", branch: "main"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/Open-Location-Stack/open-location-hub-cli/releases/download/0.1.0/olh-darwin-arm64-0.1.0.tar.gz"
      sha256 "fb5c5364838e85b7d746fdc0bebc32865f1939e8502dbe7aedeeebd85ab19ffd"
    else
      url "https://github.com/Open-Location-Stack/open-location-hub-cli/releases/download/0.1.0/olh-darwin-amd64-0.1.0.tar.gz"
      sha256 "d8cb59466606d782e935a7daaef02730f63ccb77d8a3f155e0d5c3039bd3721a"
    end
  end

  on_linux do
    if Hardware::CPU.arm?
      url "https://github.com/Open-Location-Stack/open-location-hub-cli/releases/download/0.1.0/olh-linux-arm64-0.1.0.tar.gz"
      sha256 "65a3f465c094b1e949d811068a41e0960c27fd7dda02d3d499613197f70b5a25"
    elsif Hardware::CPU.intel?
      url "https://github.com/Open-Location-Stack/open-location-hub-cli/releases/download/0.1.0/olh-linux-amd64-0.1.0.tar.gz"
      sha256 "69abd0eb8a14cec759dfcd1bde43ea5ac9c3789f114b7c2c1277aba512ce0d16"
    else
      odie "open-location-hub-cli currently publishes Homebrew binaries " \
           "for macOS arm64, macOS amd64, Linux arm64, Linux amd64 only"
    end
  end

  # STABLE-END

  depends_on "go" => :build if build.head?

  def install
    if build.head?
      ldflags = %w[
        -s
        -w
      ] + [
        "-X",
        "github.com/Open-Location-Stack/open-location-hub-cli/internal/build.Version=HEAD",
      ]
      system "go", "build", *std_go_args(ldflags: ldflags, output: bin/"olh"), "./cmd/olh"
    else
      bin.install Dir["olh-*"].first => "olh"
    end

    generate_completions_from_executable(bin/"olh", "completion")
  end

  test do
    output = shell_output("#{bin}/olh --help")
    assert_match "Open Location Hub CLI", output
  end
end

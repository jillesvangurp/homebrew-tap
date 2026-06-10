class OpenLocationHubCli < Formula
  desc "CLI for Open Location Hub"
  homepage "https://github.com/Open-Location-Stack/open-location-hub-cli"

  # STABLE-BEGIN
  version "0.1.2"
  license "MIT"
  head "https://github.com/Open-Location-Stack/open-location-hub-cli.git", branch: "main"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/Open-Location-Stack/open-location-hub-cli/releases/download/0.1.2/olh-darwin-arm64-0.1.2.tar.gz"
      sha256 "c706e3ecb58700913f55cfcae33359aeaa175ee9319de5860e3da4d019255115"
    else
      url "https://github.com/Open-Location-Stack/open-location-hub-cli/releases/download/0.1.2/olh-darwin-amd64-0.1.2.tar.gz"
      sha256 "697fb05f79a5dbf3d9f61476e898bbc2f2aac167d6b1df99c5588cea6a5271e1"
    end
  end

  on_linux do
    if Hardware::CPU.arm?
      url "https://github.com/Open-Location-Stack/open-location-hub-cli/releases/download/0.1.2/olh-linux-arm64-0.1.2.tar.gz"
      sha256 "cec7de1ad6845e7ab6779fbb8e6886fb07d18563a530feef1545a75f17453c56"
    elsif Hardware::CPU.intel?
      url "https://github.com/Open-Location-Stack/open-location-hub-cli/releases/download/0.1.2/olh-linux-amd64-0.1.2.tar.gz"
      sha256 "a24a5a59bd933bed8cca744e6d11b97bc01461745d4302716969d0d7cbd70048"
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

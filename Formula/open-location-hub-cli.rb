class OpenLocationHubCli < Formula
  desc "CLI for Open Location Hub"
  homepage "https://github.com/Open-Location-Stack/open-location-hub-cli"

  # STABLE-BEGIN
  version "0.1.4"
  license "MIT"
  head "https://github.com/Open-Location-Stack/open-location-hub-cli.git", branch: "main"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/Open-Location-Stack/open-location-hub-cli/releases/download/0.1.4/olh-darwin-arm64-0.1.4.tar.gz"
      sha256 "e8481018997b78442846479483cafb6fb97b14fea207a366ff96e46b52bc0294"
    else
      url "https://github.com/Open-Location-Stack/open-location-hub-cli/releases/download/0.1.4/olh-darwin-amd64-0.1.4.tar.gz"
      sha256 "cbf17e964dede2777094e3a4cdb6ad0b5cafb8ac7073d59a35a7a9f01b0fd22e"
    end
  end

  on_linux do
    if Hardware::CPU.arm?
      url "https://github.com/Open-Location-Stack/open-location-hub-cli/releases/download/0.1.4/olh-linux-arm64-0.1.4.tar.gz"
      sha256 "95b6721dd9aa88c4d6221781069bf1140dc0ec1340ce28e29729e7896faf4cc0"
    elsif Hardware::CPU.intel?
      url "https://github.com/Open-Location-Stack/open-location-hub-cli/releases/download/0.1.4/olh-linux-amd64-0.1.4.tar.gz"
      sha256 "d237c9ff2a2125ac06e328eb234003fa2f45c6ded8043e1c94c6e1b6234d3999"
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

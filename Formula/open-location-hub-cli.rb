class OpenLocationHubCli < Formula
  desc "CLI for Open Location Hub"
  homepage "https://github.com/Open-Location-Stack/open-location-hub-cli"

  # STABLE-BEGIN
  version "0.1.1"
  license "MIT"
  head "https://github.com/Open-Location-Stack/open-location-hub-cli.git", branch: "main"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/Open-Location-Stack/open-location-hub-cli/releases/download/0.1.1/olh-darwin-arm64-0.1.1.tar.gz"
      sha256 "eb81ee6d76dd06105ba25b1034894d0b6128938f121ce5e7749e2a85f619378e"
    else
      url "https://github.com/Open-Location-Stack/open-location-hub-cli/releases/download/0.1.1/olh-darwin-amd64-0.1.1.tar.gz"
      sha256 "170499fa0cf44812cfc5c0ee2259580e5d9964a134cd0f02ca206e0c1dc2cea6"
    end
  end

  on_linux do
    if Hardware::CPU.arm?
      url "https://github.com/Open-Location-Stack/open-location-hub-cli/releases/download/0.1.1/olh-linux-arm64-0.1.1.tar.gz"
      sha256 "ed6b982e5673296340820fc6f638c6a00870572d2879c2f8c067eb6536fa021f"
    elsif Hardware::CPU.intel?
      url "https://github.com/Open-Location-Stack/open-location-hub-cli/releases/download/0.1.1/olh-linux-amd64-0.1.1.tar.gz"
      sha256 "f98a20f6eae2e9e809e5c5d856589facf92c26592ca27aa0f5976d482c62eef8"
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

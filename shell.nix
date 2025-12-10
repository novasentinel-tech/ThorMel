{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    (pkgs.python3.withPackages (ps: with ps; [
      aiohttp
      beautifulsoup4
      cryptography
      dnspython
      fake-useragent
      psutil
      pysocks
      requests
      schedule
      stem
      urllib3
      websockets
    ]))
  ];
}

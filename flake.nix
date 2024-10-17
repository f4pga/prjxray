{
  description = "prjxray";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
      pythonEnv = pkgs.python3.withPackages(ps: [ ]);
    in {
      devShells.x86_64-linux.default = pkgs.mkShell {
        packages = [
          pkgs.cmake
          pythonEnv
        ];
        shellHook = ''
        make build
        python -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
        make db-prepare-parts
        ./download-latest-db.sh
        '';
      };
    };
}

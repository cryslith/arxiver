{
  outputs = { self, nixpkgs }: let
    system = "x86_64-linux";
    pkgs = import nixpkgs {inherit system;};
    arxiver-py = (ps: with ps; (
      ps.buildPythonPackage rec {
        pname = "arxiver";
        version = "0.0.1";
        src = ./.;
        pyproject = true;
        nativeBuildInputs = [ ps.hatchling ];
        pythonImportsCheck = [ pname ];
      }
    )) pkgs.python3Packages;
  in {
    packages.${system}.default = arxiver-py;
    apps.${system} = {
      arxiver = {
        type = "app";
        program = "${arxiver-py}/bin/arxiver";
      };
      strip-comments = {
        type = "app";
        program = "${arxiver-py}/bin/strip-comments";
      };
    };
    devShells.${system}.default = pkgs.mkShell {
      packages = [
        arxiver-py
      ];
    };
  };
}

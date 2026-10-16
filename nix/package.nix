{
  lib,
  stdenv,
  makeWrapper,
  fastfetch,
  # linux-only
  pciutils,
}:

stdenv.mkDerivation (finalAttrs: {
  pname = "ffetch-3d";
  version = lib.fileContents ../VERSION;
  __structuredAttrs = true;
  strictDeps = true;

  src = lib.cleanSource ../.;

  makeFlags = [ "PREFIX=${placeholder "out"}" ];
  nativeBuildInputs = [ makeWrapper ];
  postInstall = ''
    wrapProgram $out/bin/ffetch-3d \
    --prefix PATH : ${
      lib.makeBinPath ([ fastfetch ] ++ lib.optionals stdenv.hostPlatform.isLinux [ pciutils ])
    }
  '';

  meta = {
    description = "Animated 3D terminal logos with synchronized neon RGB colors";
    license = lib.licenses.isc;
    mainProgram = "ffetch-3d";
    platforms = lib.platforms.unix;
  };
})

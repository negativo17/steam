%global debug_package %{nil}
%global appstream_id com.valvesoftware.Steam

Name:           steam
Version:        1.0.0.85
Release:        10%{?dist}
Summary:        Installer for the Steam software distribution service
# Redistribution and repackaging for Linux is allowed, see license file
License:        Steam License Agreement
URL:            http://www.steampowered.com/
ExclusiveArch:  x86_64

Source0:        https://repo.steampowered.com/%{name}/archive/beta/%{name}_%{version}.tar.gz
Source1:        %{name}.sh
Source2:        %{name}.csh
Source3:        README.Fedora
# Configure limits in systemd
Source7:        01-steam.conf

# Do not install desktop file in lib/steam, do not install apt sources
Patch0:         %{name}-makefile.patch
# Do not try to copy steam.desktop to the user's desktop from lib/steam
Patch1:         %{name}-no-icon-on-desktop.patch

BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
BuildRequires:  make
BuildRequires:  systemd

# Required for the basic runtime
Requires:       glibc(x86-32)
Requires:       libdrm(x86-32)
Requires:       libglvnd-glx(x86-32)
Requires:       libnsl(x86-32)

# Required to run the initial setup
Requires:       tar
Requires:       zenity
Requires:       xz

# Required for basic gaming, also for native 32 bit games:
Requires:       mesa-dri-drivers
Requires:       mesa-dri-drivers(x86-32)
Requires:       mesa-vulkan-drivers
Requires:       mesa-vulkan-drivers(x86-32)
Requires:       vulkan-loader
Requires:       vulkan-loader(x86-32)

# Hardware stuff (permissions on devices, hardware updater, etc.):
Recommends:     hidapi
Requires:       steam-devices

# These libraries are also part of the Ubuntu runtime at:
#   ~/.local/share/Steam/ubuntu12_32
#   ~/.local/share/Steam/ubuntu12_64
# Steam client uses the system ones if available; so override where there is a
# benefit using the native system libaries or just to match when the native 64
# bit packages are already installed.
Requires:       bzip2-libs
Requires:       bzip2-libs(x86-32)
Requires:       fontconfig
Requires:       fontconfig(x86-32)
Requires:       libICE
Requires:       libICE(x86-32)
Requires:       libnsl
Requires:       libnsl(x86-32)
#Requires:       libpng
#Requires:       libpng(x86-32)
Requires:       libXext
Requires:       libXext(x86-32)
Requires:       libXinerama
Requires:       libXinerama(x86-32)
Requires:       libXtst
Requires:       libXtst(x86-32)
Requires:       libva
Requires:       libva(x86-32)
Requires:       libvdpau
Requires:       libvdpau(x86-32)
Requires:       mesa-libGL
Requires:       mesa-libGL(x86-32)
Requires:       NetworkManager-libnm
Requires:       NetworkManager-libnm(x86-32)
Requires:       nss
Requires:       nss(x86-32)
Requires:       openal-soft
Requires:       openal-soft(x86-32)
Requires:       pipewire-libs
Requires:       pipewire-libs(x86-32)
Requires:       pulseaudio-libs
Requires:       pulseaudio-libs(x86-32)
%if 0%{?fedora}
Requires:       SDL3
Requires:       SDL3(x86-32)
%endif
# The client does not override only the ones linked at:
#   ~/.local/share/Steam/ubuntu12_32/steam-runtime/pinned_libs_32
#   ~/.local/share/Steam/ubuntu12_32/steam-runtime/pinned_libs_64
# At the moment of writing, the pinned ones belong to these packages:
#   gtk2
#   libcurl
#   libdbusmenu
#   libdbusmenu-gtk2
#   mesa-libGLU
# And yes, the "ubuntu12_32" directory twice above is not a typo. Windows style (system32...).

# Required for the firewall rules
# http://fedoraproject.org/wiki/PackagingDrafts/ScriptletSnippets/Firewalld
Requires:       firewalld-filesystem
Requires(post): firewalld-filesystem

# Required by Feral interactive games
Requires:       libatomic
Requires:       libatomic(x86-32)

# Required by Shank
Requires:       (alsa-plugins-pulseaudio if pulseaudio)

# Game performance is increased with gamemode (for games that support it)
Recommends:     gamemode
Recommends:     (gnome-shell-extension-appindicator if gnome-shell)

# Proton uses xdg-desktop-portal to open URLs from inside a container
Requires:       xdg-desktop-portal
Recommends:     (xdg-desktop-portal-gtk if gnome-shell)
Recommends:     (xdg-desktop-portal-kde if kwin)

# Prevent log spam when thse are not pulled in as dependencies of full desktops
Recommends:     dbus-x11
Recommends:     xdg-user-dirs

# Allow using Steam Runtime Launch Options
Recommends:     gobject-introspection

# Automatic loading of the ntsync module
Recommends:     ntsync-autoload

%description
Steam is a software distribution service with an online store, automated
installation, automatic updates, achievements, SteamCloud synchronized savegame
and screenshot functionality, and many social features.

This package contains the installer for the Steam software distribution service.

%package arch-transition
Summary: Transition package for migrating Steam from i686 to x86_64
Requires: %{name} = %{version}-%{release}
Provides: steam = 1.0.0.85-8
Obsoletes: steam < 1.0.0.85-8
BuildArch: noarch

%description arch-transition
This package is used to migrate Steam installations from the
legacy i686 package layout to the x86_64 package layout.

It exists only to handle package replacement and dependency
changes during upgrades, and can be safely removed once the
transition is complete.

%prep
%autosetup -p1 -n %{name}-launcher

cp %{SOURCE3} .

%build
# Nothing to build

%install
%make_install

rm -fr \
    %{buildroot}%{_docdir}/%{name}/ \
    %{buildroot}%{_bindir}/%{name}deps

# Environment files
mkdir -p %{buildroot}%{_sysconfdir}/profile.d
install -pm 644 %{SOURCE1} %{SOURCE2} %{buildroot}%{_sysconfdir}/profile.d

# Raise file descriptor limit
mkdir -p %{buildroot}%{_prefix}/lib/systemd/system.conf.d/
mkdir -p %{buildroot}%{_prefix}/lib/systemd/user.conf.d/
install -m 644 -p %{SOURCE7} %{buildroot}%{_prefix}/lib/systemd/system.conf.d/
install -m 644 -p %{SOURCE7} %{buildroot}%{_prefix}/lib/systemd/user.conf.d/

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/%{appstream_id}.metainfo.xml

%files
%license COPYING steam_subscriber_agreement.txt
%doc debian/changelog README.Fedora
%{_bindir}/%{name}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/pixmaps/%{name}.png
%{_datadir}/pixmaps/%{name}_tray_mono.png
%{_prefix}/lib/%{name}/
%{_mandir}/man6/%{name}.*
%{_metainfodir}/%{appstream_id}.metainfo.xml
%config(noreplace) %{_sysconfdir}/profile.d/%{name}.*sh
%dir %{_prefix}/lib/systemd/system.conf.d/
%{_prefix}/lib/systemd/system.conf.d/01-steam.conf
%dir %{_prefix}/lib/systemd/user.conf.d/
%{_prefix}/lib/systemd/user.conf.d/01-steam.conf

%files arch-transition

%changelog
* Tue May 26 2026 Sérgio Basto <sergio@serjux.com> - 1.0.0.85-10
- Add steam-arch-transition package for i686 to x86_64 migration.

* Thu May 21 2026 Simone Caronni <negativo17@gmail.com> - 1.0.0.85-9
- Recommend hidapi as it's temporary and in the devel repository for RHEL.

* Thu May 21 2026 Simone Caronni <negativo17@gmail.com> - 1.0.0.85-8
- RHEL does not have SDL3 packages, and the client is all SDL3 based.

* Wed May 20 2026 Simone Caronni <negativo17@gmail.com> - 1.0.0.85-7
- Package is now x86_64 as the client itself is all 64 bit based.
- Most of the client libraries are also installed in 32 bit format, as all the
  client features compiled into the games still require them. For the same
  reason, 32 bit graphics libraries are also required.
- Override client libraries using system ones where it makes sense.
- Requires hidapi for the the new hardware updater (#7452).

* Mon Apr 13 2026 Simone Caronni <negativo17@gmail.com> - 1.0.0.85-6
- Drop certificate workaround:
  https://bodhi.fedoraproject.org/updates/FEDORA-2026-285c6d38f7

* Mon Mar 16 2026 Simone Caronni <negativo17@gmail.com> - 1.0.0.85-5
- Change %post condition in Fedora 44 to triggerin.

* Thu Feb 19 2026 Simone Caronni <negativo17@gmail.com> - 1.0.0.85-4
- Apply workaround for
  https://fedoraproject.org/wiki/Changes/droppingOfCertPemFile.

* Fri Jan 16 2026 Simone Caronni <negativo17@gmail.com> - 1.0.0.85-3
- Requires xz for initial setup.

* Wed Nov 26 2025 Simone Caronni <negativo17@gmail.com> - 1.0.0.85-2
- Do not provide ntsync loading mechanism, require the ntsync-autoload package
  (ntsync is not yet enabled in official Proton versions).

* Fri Oct 17 2025 Simone Caronni <negativo17@gmail.com> - 1.0.0.85-1
- Update to 1.0.0.85.

* Sun Sep 07 2025 Simone Caronni <negativo17@gmail.com> - 1.0.0.83-2
- Load ntsync module.

* Sat May 10 2025 Simone Caronni <negativo17@gmail.com> - 1.0.0.83-1
- Update to 1.0.0.83.

* Thu Mar 20 2025 Simone Caronni <negativo17@gmail.com> - 1.0.0.82-2
- Drop steam-devices subpackage.
- Update README.Fedora.
- Trim changelog.

* Mon Nov 04 2024 Simone Caronni <negativo17@gmail.com> - 1.0.0.82-1
- Update to 1.0.0.82.

* Sun Sep 01 2024 Simone Caronni <negativo17@gmail.com> - 1.0.0.81-1
- Update to 1.0.0.81.

* Mon Aug 05 2024 Simone Caronni <negativo17@gmail.com> - 1.0.0.79-6
- Fix for #9 (thanks zeroepoch).

* Mon Jun 24 2024 Simone Caronni <negativo17@gmail.com> - 1.0.0.79-5
- Update udev rules.
- Convert udev rule for blocking wrong joystick devices to a systemd hwdb file:
  https://github.com/denilsonsa/udev-joystick-blacklist/issues/58

* Mon Jun 24 2024 Simone Caronni <negativo17@gmail.com> - 1.0.0.79-4
- Add dependencies when full desktop is not installed.
- Add dependencies for using steam-runtime-launch-options.

* Tue Mar 19 2024 Simone Caronni <negativo17@gmail.com> - 1.0.0.79-3
- Adjust requirements.

* Sun Feb 18 2024 Simone Caronni <negativo17@gmail.com> - 1.0.0.79-2
- Do not recommend gnome-shell-extension-gamemode.

* Mon Feb 12 2024 Simone Caronni <negativo17@gmail.com> - 1.0.0.79-1
- Update to 1.0.0.79.

* Mon Jan 22 2024 Simone Caronni <negativo17@gmail.com> - 1.0.0.78-2
- Update udev rules.

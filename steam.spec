# Binary package, no debuginfo should be generated
%global debug_package %{nil}

# If firewalld macro is not defined, define it here:
%{!?firewalld_reload:%global firewalld_reload test -f /usr/bin/firewall-cmd && firewall-cmd --reload --quiet || :}

Name:           steam
Version:        1.0.0.54
Release:        9%{?dist}
Summary:        Installer for the Steam software distribution service
# Redistribution and repackaging for Linux is allowed, see license file
License:        Steam License Agreement
URL:            http://www.steampowered.com/
ExclusiveArch:  i686

Source0:        http://repo.steampowered.com/%{name}/pool/%{name}/s/%{name}/%{name}_%{version}.tar.gz
Source1:        %{name}.sh
Source2:        %{name}.csh
Source3:        %{name}.xml
Source4:        %{name}.appdata.xml

# Ghost touches in Big Picture mode:
# https://github.com/ValveSoftware/steam-for-linux/issues/3384
# https://bugzilla.kernel.org/show_bug.cgi?id=28912
# https://github.com/denilsonsa/udev-joystick-blacklist

# Input devices seen as joysticks:
Source8:        https://raw.githubusercontent.com/denilsonsa/udev-joystick-blacklist/master/after_kernel_4_9/51-these-are-not-joysticks-rm.rules
# First generation Nvidia Shield controller seen as mouse:
Source9:        https://raw.githubusercontent.com/cyndis/shield-controller-config/master/99-shield-controller.rules

Source10:       README.Fedora

# Remove temporary leftover files after run (fixes multiuser):
# https://github.com/ValveSoftware/steam-for-linux/issues/3570
Patch0:         %{name}-3570.patch

# Make Steam Controller usable as a GamePad:
# https://steamcommunity.com/app/353370/discussions/0/490123197956024380/
Patch1:         %{name}-controller-gamepad-emulation.patch

BuildRequires:  desktop-file-utils
BuildRequires:  systemd

# Required to run the initial setup
Requires:       tar
Requires:       zenity

# Required for S3 compressed textures on free drivers (intel/radeon/nouveau)
Requires:       libtxc_dxtn%{?_isa}

# Required for running the package on 32 bit systems with free drivers
Requires:       mesa-dri-drivers%{?_isa}

# Minimum requirements for starting the steam client for the first time
Requires:       alsa-lib%{?_isa}
Requires:       gtk2%{?_isa}
Requires:       libpng12%{?_isa}
Requires:       libXext%{?_isa}
Requires:       libXinerama%{?_isa}
Requires:       libXtst%{?_isa}
Requires:       libXScrnSaver%{?_isa}
Requires:       mesa-libGL%{?_isa}
Requires:       nss%{?_isa}
Requires:       pulseaudio-libs%{?_isa}

# Required for sending out crash reports to Valve
Requires:       libcurl%{?_isa}

# Workaround for mesa-libGL dependency bug:
# https://bugzilla.redhat.com/show_bug.cgi?id=1168475
Requires:       systemd-libs%{?_isa}

# Required for the firewall rules
# http://fedoraproject.org/wiki/PackagingDrafts/ScriptletSnippets/Firewalld
%if 0%{?rhel}
Requires:       firewalld
Requires(post): firewalld
%else
Requires:       firewalld-filesystem
Requires(post): firewalld-filesystem
%endif

# Required for hardware decoding during In-Home Streaming (intel)
Requires:       libva-intel-driver%{?_isa}

# Required for hardware decoding during In-Home Streaming (radeon/nouveau)
Requires:       libvdpau%{?_isa}

# Required for having a functioning menu on the tray icon
Requires:       libdbusmenu-gtk2%{?_isa} >= 16.04.0
Requires:       libdbusmenu-gtk3%{?_isa} >= 16.04.0

Provides:       steam-noruntime = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      steam-noruntime < %{?epoch:%{epoch}:}%{version}-%{release}

%description
Installer for the Steam software distribution service.
Steam is a software distribution service with an online store, automated
installation, automatic updates, achievements, SteamCloud synchronized savegame
and screenshot functionality, and many social features.

%prep
%setup -q -n %{name}
%patch0 -p1
%patch1 -p1

sed -i 's/\r$//' %{name}.desktop
sed -i 's/\r$//' steam_install_agreement.txt

cp %{SOURCE10} .

%build
# Nothing to build

%install
%make_install

rm -fr %{buildroot}%{_docdir}/%{name}/ \
    %{buildroot}%{_bindir}/%{name}deps

mkdir -p %{buildroot}%{_udevrulesdir}/
install -m 644 -p lib/udev/rules.d/* \
    %{SOURCE8} %{SOURCE9} %{buildroot}%{_udevrulesdir}/

desktop-file-validate %{buildroot}/%{_datadir}/applications/%{name}.desktop

install -D -m 644 -p %{SOURCE3} \
    %{buildroot}%{_prefix}/lib/firewalld/services/steam.xml

# Environment files
mkdir -p %{buildroot}%{_sysconfdir}/profile.d
install -pm 644 %{SOURCE1} %{SOURCE2} %{buildroot}%{_sysconfdir}/profile.d

%if 0%{?fedora} >= 25
# Install AppData
mkdir -p %{buildroot}%{_datadir}/appdata
install -p -m 0644 %{SOURCE4} %{buildroot}%{_datadir}/appdata/
%endif

%post
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
%if 0%{?fedora} == 24 || 0%{?rhel} == 7
/usr/bin/update-desktop-database &> /dev/null || :
%endif
%firewalld_reload

%postun
%if 0%{?fedora} == 24 || 0%{?rhel} == 7
/usr/bin/update-desktop-database &> /dev/null || :
%endif
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    %{_bindir}/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
%{_bindir}/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files
%license COPYING steam_install_agreement.txt
%doc README debian/changelog README.Fedora
%{_bindir}/%{name}
%if 0%{?fedora} >= 25
%{_datadir}/appdata/%{name}.appdata.xml
%endif
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/pixmaps/%{name}.png
%{_datadir}/pixmaps/%{name}_tray_mono.png
%{_libdir}/%{name}/
%{_mandir}/man6/%{name}.*
%{_prefix}/lib/firewalld/services/%{name}.xml
%config(noreplace) %{_sysconfdir}/profile.d/%{name}.*sh
%{_udevrulesdir}/*

%changelog
* Wed Apr 19 2017 Simone Caronni <negativo17@gmail.com> - 1.0.0.54-9
- GTK 2/3 version of libdbusmenu at version 16.04.0 is required for a working
  tray menu depending on the desktop.

* Mon Apr 10 2017 Simone Caronni <negativo17@gmail.com> - 1.0.0.54-8
- Update udev rules.

* Sun Feb 12 2017 Simone Caronni <negativo17@gmail.com> - 1.0.0.54-7
- Remove libstdc++ patch.
- Update udev rules.
- Update docs for hardware encoding/decoding information.

* Fri Feb 10 2017 Simone Caronni <negativo17@gmail.com> - 1.0.0.54-6
- Remove patch for window button behaviour, use shell profile.

* Fri Feb 10 2017 Simone Caronni <negativo17@gmail.com> - 1.0.0.54-5
- Luckily the libdbusmenu-gtk3 library is required only on Fedora and not
  RHEL/CentOS.

* Fri Feb 10 2017 Simone Caronni <negativo17@gmail.com> - 1.0.0.54-4
- Remove noruntime subpackage, use default new mechanism that uses host
  libraries as per client update of 19th January (5th January for beta):
  http://store.steampowered.com/news/26953/

* Sun Jan 08 2017 Simone Caronni <negativo17@gmail.com> - 1.0.0.54-3
- Microsoft keyboards have been fixed in kernel 4.9 and backported to other
  kernels.

* Tue Dec 13 2016 Simone Caronni <negativo17@gmail.com> - 1.0.0.54-2
- Re-add close functionality to X window button (#3210).

* Mon Nov 28 2016 Simone Caronni <negativo17@gmail.com> - 1.0.0.54-1
- Update to 1.0.0.54.
- Update udev patch.

* Wed Oct 26 2016 Simone Caronni <negativo17@gmail.com> - 1.0.0.53-1
- Update to 1.0.0.53.
- Update udev rules.

* Fri Sep 23 2016 Simone Caronni <negativo17@gmail.com> - 1.0.0.52-5
- Updated AppStream metadata.

* Sun Sep 11 2016 Simone Caronni <negativo17@gmail.com> - 1.0.0.52-4
- Do not run update-desktop-database on Fedora 25+.
- Add AppStream metadata.

* Sat Aug 13 2016 Simone Caronni <negativo17@gmail.com> - 1.0.0.52-3
- Make Steam Controller usable as a gamepad (#4062).
- Update UDev rule for keyboards detected as joysticks.
- Update README.Fedora file with notes about the Steam Controller, its update
  process and update the list of devices with UDev rules.

* Wed May 25 2016 Simone Caronni <negativo17@gmail.com> - 1.0.0.52-2
- Remove freetype-freeworld as a dependency for the noruntime subpackage.

* Fri Apr 01 2016 Simone Caronni <negativo17@gmail.com> - 1.0.0.52-1
- Update to 1.0.0.52, adds HTC Vive udev rules.
- Move hardware accelerated streaming requirements to main package.

* Thu Feb 25 2016 Simone Caronni <negativo17@gmail.com> - 1.0.0.51-6
- Update UDev blacklist.
- Update README.Fedora, SELinux boolean no longer required.

* Thu Feb 25 2016 Simone Caronni <negativo17@gmail.com> - 1.0.0.51-5
- Apply #3273 workaround only on systems where Mesa has not been statically
  compiled with libstdc++ (mesa-11.1.0-2.20151218.fc23+).

* Mon Feb 01 2016 Simone Caronni <negativo17@gmail.com> - 1.0.0.51-4
- Fix blacklist udev rules.
- Add support for Nvidia Shield Controller.
- Update README.Fedora accordingly.

* Sun Jan 31 2016 Simone Caronni <negativo17@gmail.com> - 1.0.0.51-3
- Add UDev rules for keyboards detected as joysticks:
  https://github.com/ValveSoftware/steam-for-linux/issues/3384
  https://bugzilla.kernel.org/show_bug.cgi?id=28912
  https://github.com/denilsonsa/udev-joystick-blacklist

* Sun Dec 06 2015 Simone Caronni <negativo17@gmail.com> - 1.0.0.51-2
- Update requirements.

* Fri Nov 20 2015 Simone Caronni <negativo17@gmail.com> - 1.0.0.51-1
- Update to 1.0.0.51.
- Updated udev rules for the Steam Controller and HTC Vive VR headset.
- Update isa requirements.

* Wed Nov 18 2015 Simone Caronni <negativo17@gmail.com> - 1.0.0.50-8
- Remove Compiz and Emerald dependencies from noruntime.

* Sat Oct 31 2015 Simone Caronni <negativo17@gmail.com> - 1.0.0.50-7
- Update requirements for Fedora 23+.

* Thu Jul 09 2015 Simone Caronni <negativo17@gmail.com> - 1.0.0.50-4
- Integrate FirewallD rules.
- Add requirement on firewalld for CentOS/RHEL and on firewalld-filesystem
  for Fedora.

* Wed Jul 08 2015 Simone Caronni <negativo17@gmail.com> - 1.0.0.50-3
- Re-add support for the noruntime subpackage (not for CentOS/RHEL).
- Integrate patches in noruntime patch.
- In-Home streaming requirements:
    libva-intel-driver (intel)
    libvdpau (nouveau/radeon)
- Updated README.Fedora for In-Home streaming.

* Mon May 25 2015 Simone Caronni <negativo17@gmail.com> - 1.0.0.50-2
- Add license macro.
- Add workaround for bug 3273, required for running client/games with prime:
  https://github.com/ValveSoftware/steam-for-linux/issues/3273

* Thu May 07 2015 Simone Caronni <negativo17@gmail.com> - 1.0.0.50-1
- Update to 1.0.0.50.
- Add new requirements; update README file.

* Mon Jan 12 2015 Simone Caronni <negativo17@gmail.com> - 1.0.0.49-4
- Flash plugin is no longer required for playing videos in the store, update
  README.Fedora.

* Thu Jan 08 2015 Simone Caronni <negativo17@gmail.com> - 1.0.0.49-3
- Workaround for bug 3570:
  https://github.com/ValveSoftware/steam-for-linux/issues/3570

* Tue Dec 02 2014 Simone Caronni <negativo17@gmail.com> - 1.0.0.49-2
- Update requirements.

* Wed Aug 27 2014 Simone Caronni <negativo17@gmail.com> - 1.0.0.49-1
- Update to 1.0.0.49.

* Tue Jul 29 2014 Simone Caronni <negativo17@gmail.com> - 1.0.0.48-3
- Obsolete noruntime subpackage.

* Mon Jun 23 2014 Simone Caronni <negativo17@gmail.com> - 1.0.0.48-2
- Add additional libraries required by games when skipping runtime.

* Thu Jun 19 2014 Simone Caronni <negativo17@gmail.com> - 1.0.0.48-1
- Update to 1.0.0.48.

* Thu May 15 2014 Simone Caronni <negativo17@gmail.com> - 1.0.0.47-4
- Update noruntime subpackage requirements.

* Mon May 05 2014 Simone Caronni <negativo17@gmail.com> - 1.0.0.47-3
- Add new libbz2.so requirement.

* Tue Apr 01 2014 Simone Caronni <negativo17@gmail.com> - 1.0.0.47-2
- Close window when clicking the x button (#3210).

* Wed Feb 12 2014 Simone Caronni <negativo17@gmail.com> - 1.0.0.47-1
- Update to 1.0.0.47.

* Mon Jan 06 2014 Simone Caronni <negativo17@gmail.com> - 1.0.0.45-6
- Make noruntime subpackage noarch.

* Mon Jan 06 2014 Simone Caronni <negativo17@gmail.com> - 1.0.0.45-5
- Update README.Fedora with new instructions.

* Mon Jan 06 2014 Simone Caronni <negativo17@gmail.com> - 1.0.0.45-4
- Create a no-runtime subpackage leaving the main package to behave as intended
  by Valve. All the Steam Runtime dependencies are against the subpackage.

* Mon Dec 23 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.45-3
- Additional system libraries required by games.

* Fri Dec 20 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.45-2
- If STEAM_RUNTIME is not set, perform the following actions by default from the
  main commmand:
    Disable the Ubuntu runtime.
    Delete the unpacked Ubuntu runtime.
    Create the obsolete libudev.so.0.

* Wed Nov 27 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.45-1
- Update to 1.0.0.45.

* Thu Nov 14 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.44-1
- Update to 1.0.0.44.

* Fri Nov 08 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.43-9
- Disable STEAM_RUNTIME, drop all requirements and change README.Fedora. Please
  see for details:
    https://github.com/ValveSoftware/steam-for-linux/issues/2972
    https://github.com/ValveSoftware/steam-for-linux/issues/2976
    https://github.com/ValveSoftware/steam-for-linux/issues/2978

* Mon Nov 04 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.43-8
- Add missing mesa-dri-drivers requirement.

* Mon Oct 28 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.43-7
- Added libXScrnSaver to requirements.

* Wed Oct 23 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.43-6
- Rpmlint review fixes.

* Wed Oct 23 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.43-5
- Do not remove buildroot in install section.
- Update desktop database after installation/uninstallation.

* Tue Oct 22 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.43-4
- Added systemd build requirement for udev rules.

* Sun Oct 20 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.43-3
- Add alsa-plugins-pulseaudio to requirements.
- Add libappindicator to requirements to enable system tray icon.

* Thu Oct 10 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.43-2
- Remove requirements pulled in by other components.

* Wed Oct 09 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.43-1
- Update to 1.0.0.43.

* Thu Oct 03 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.42-2
- Remove rpmfusion repository dependency.

* Wed Sep 11 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.42-1
- Update to 1.0.0.42.

* Sun Sep 08 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.41-1
- Update to 1.0.0.41.

* Thu Aug 29 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.40-1
- Update to 1.0.0.40.
- Add Steam controller support.

* Sun Aug 18 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.39-5
- Rework requirements section.
- Add tar and zenity requirements for initial setup.

* Mon Aug 05 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.39-4
- Remove Fedora 17 as it is now EOL.

* Wed May 29 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.39-3
- Add STEAM_RUNTIME=0 to profile settings.

* Mon May 13 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.39-2
- Added NetworkManager requirement for STEAM_RUNTIME=0.

* Mon May 13 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.39-1
- Updated to 1.0.0.39.

* Thu May 09 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.38-2
- Changed Fedora 19 FLAC requirements.

* Sun Apr 28 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.38-1
- Updated to 1.0.0.38.

* Fri Apr 19 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.36-2
- Add additional libraries for starting with STEAM_RUNTIME=0.
- Added README.Fedora document with additional instructions.

* Fri Mar 15 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.36-1
- Update to 1.0.0.36.

* Mon Mar 04 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.35-1
- Updated.

* Mon Feb 25 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.34-1
- Update to 1.0.0.34.

* Thu Feb 21 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.29-2
- Added changelog to docs.

* Thu Feb 21 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.29-1
- Updated.

* Fri Feb 15 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.27-1
- Updated, used official install script.
- Removed patch.

* Mon Feb 11 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.25-1
- Updated to 1.0.0.25.
- Reworked installation for new tar package.
- Used official docs.

* Tue Jan 22 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.22-3
- Moved documents to the default document directory.
- Use internal license file instead of provided one.
- Removed STEAMSCRIPT modification, fixed in 1.0.0.22.

* Tue Jan 22 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.22-1
- Updated.

* Thu Jan 17 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.21-2
- Sorted Requires.
- Fix STEAMSCRIPT_VERSION.
- Added RPMFusion free repository as requirement for libtxc_dxtn (or nvidia drivers...).

* Thu Jan 17 2013 Simone Caronni <negativo17@gmail.com> - 1.0.0.21-1
- Updated version, patch and tarball generation for 1.0.0.21.
- Added libtxc_dxtn requirement (rpmfusion).
- Replaced steam with %%{name} where it fits.
- Removed jpeg library hack.
- Removed SDL2 requirement, is downloaded by the client.
- Replace (x86-32) with %%{_isa}.

* Tue Jan 8 2013 Tom Callaway <spot@fedoraproject.org> - 1.0.0.18-1
- update to 1.0.0.18

* Wed Nov 7 2012 Tom Callaway <spot@fedoraproject.org> - 1.0.0.14-3
- add more Requires (from downloaded bits, not packaged bits)

* Tue Nov 6 2012 Tom Callaway <spot@fedoraproject.org> - 1.0.0.14-2
- fedora specific libpng conditionalization

* Tue Nov 6 2012 Tom Callaway <spot@fedoraproject.org> - 1.0.0.14-1
- initial Fedora RPM packaging

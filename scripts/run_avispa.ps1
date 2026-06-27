param(
  [string]$VmName = $env:AVISPA_VM_NAME,
  [string]$VmUser = $env:AVISPA_VM_USER,
  [string]$VmPassword = $env:AVISPA_VM_PASSWORD,
  [string]$VBoxManage = $env:VBOXMANAGE_PATH
)

$ErrorActionPreference = 'Stop'

if (-not $VmName) { $VmName = 'SPAN-Ubuntu10.10-light' }
if (-not $VmUser) { $VmUser = 'span' }
if (-not $VmPassword) { $VmPassword = 'span' }

if (-not $VBoxManage) {
  $vboxCmd = Get-Command VBoxManage.exe -ErrorAction SilentlyContinue
  if (-not $vboxCmd) {
    foreach ($candidate in @(
      'C:\Program Files\Oracle\VirtualBox\VBoxManage.exe',
      'C:\Program Files (x86)\Oracle\VirtualBox\VBoxManage.exe'
    )) {
      if (Test-Path $candidate) {
        $vboxCmd = Get-Item $candidate
        break
      }
    }
  }
  if (-not $vboxCmd) {
    throw 'VBoxManage.exe was not found. Install Oracle VirtualBox or set VBOXMANAGE_PATH.'
  }
  $VBoxManage = $vboxCmd.FullName
}

$running = & $VBoxManage list runningvms
if ($LASTEXITCODE -ne 0) {
  throw 'Failed to query running VirtualBox VMs.'
}

if ($running -notmatch [regex]::Escape($VmName)) {
  throw "VM '$VmName' is not running."
}

$arguments = @(
  'guestcontrol',
  $VmName,
  'run',
  '--exe', '/bin/bash',
  '--username', $VmUser,
  '--password', $VmPassword,
  '--wait-stdout',
  '--wait-stderr',
  '--',
  '/home/span/Desktop/share_AVISPA/scripts/run_avispa.sh'
)

& $VBoxManage @arguments
exit $LASTEXITCODE

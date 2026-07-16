# Verify OpenGate repo + release ZIP layout against release_inventory.txt.
# Run after every version bump, before/after build_release.ps1.
# Usage (from repo root): .\verify_release.ps1 [-ZipPath dist\opengate-0.3.3.zip]

param(
    [string]$ZipPath = ""
)

$ErrorActionPreference = "Stop"

$RepoRoot = $PSScriptRoot
$InventoryPath = Join-Path $RepoRoot "release_inventory.txt"
$ManifestPath = Join-Path $RepoRoot "blender_manifest.toml"
$ReadmePath = Join-Path $RepoRoot "README.md"

if (-not (Test-Path $InventoryPath)) {
    throw "Missing release_inventory.txt in $RepoRoot"
}

$expected = Get-Content $InventoryPath |
    Where-Object { $_ -and -not $_.StartsWith("#") } |
    ForEach-Object { $_.Trim().Replace("\", "/") }

if ($expected.Count -eq 0) {
    throw "release_inventory.txt contains no file paths"
}

$allowedGitOnly = @(
    ".gitignore",
    "release_inventory.txt",
    "verify_release.ps1"
)

$forbiddenZipFragments = @(
    "/development/",
    "/docs/",
    "/.git/",
    "/__pycache__/",
    "/dist/",
    "MASK_COMBO_MATRIX.md",
    "build_release.ps1",
    "verify_release.ps1",
    "release_inventory.txt",
    ".gitignore",
    "sync.ffs_db",
    ".DS_Store",
    "Thumbs.db",
    "opengate-combo-"
)

$failures = @()

function Add-Failure {
    param([string]$Message)
    $script:failures += $Message
}

Write-Host "OpenGate release verification"
Write-Host "  Inventory: $($expected.Count) payload files"

# --- Repo: payload files exist on disk ---
foreach ($rel in $expected) {
    $full = Join-Path $RepoRoot ($rel -replace "/", [IO.Path]::DirectorySeparatorChar)
    if (-not (Test-Path -LiteralPath $full)) {
        Add-Failure "Missing on disk: $rel"
    }
}

# --- Repo: git tracking matches inventory + allowed extras ---
$gitFiles = git -C $RepoRoot ls-files | ForEach-Object { $_.Replace("\", "/") } | Sort-Object
$expectedSet = [System.Collections.Generic.HashSet[string]]::new([string[]]$expected)
$allowedSet = [System.Collections.Generic.HashSet[string]]::new([string[]]($expected + $allowedGitOnly))

foreach ($rel in $expected) {
    if ($gitFiles -notcontains $rel) {
        Add-Failure "Not git-tracked: $rel"
    }
}

foreach ($tracked in $gitFiles) {
    if (-not $allowedSet.Contains($tracked)) {
        Add-Failure "Unexpected git-tracked file: $tracked"
    }
}

# --- Manifest + README version alignment ---
if (-not (Test-Path $ManifestPath)) {
    Add-Failure "Missing blender_manifest.toml"
}
else {
    $manifest = Get-Content $ManifestPath -Raw
    if ($manifest -notmatch '(?m)^version\s*=\s*"(?<ver>[^"]+)"') {
        Add-Failure "Could not read version from blender_manifest.toml"
    }
    else {
        $manifestVersion = $Matches.ver
        $readme = Get-Content $ReadmePath -Raw
        if ($readme -notmatch "\*\*Version $([regex]::Escape($manifestVersion))\*\*") {
            Add-Failure "README.md version does not match blender_manifest.toml ($manifestVersion)"
        }
        if ($manifest -match '(?m)^maintainer\s*=\s*"[^"]*<[^>]+>[^"]*"') {
            Add-Failure "blender_manifest.toml maintainer uses angle brackets (Superhive incompatible)"
        }
        if ($manifest -match '(?m)^maintainer\s*=\s*"[^"]*\([^)]*@[^)]+\)[^"]*"') {
            Add-Failure "blender_manifest.toml maintainer uses parentheses around email (Superhive incompatible)"
        }
        if ($manifest -notmatch '(?m)^maintainer\s*=\s*"[^"]*//\s*[^"]+@[^"]+"') {
            Add-Failure "blender_manifest.toml maintainer should use '// email@example.com' format for Superhive"
        }
        if (-not $ZipPath) {
            $ZipPath = Join-Path $RepoRoot "dist\opengate-$manifestVersion.zip"
        }
    }
}

# --- ZIP layout ---
if (-not (Test-Path -LiteralPath $ZipPath)) {
    Add-Failure "Release ZIP not found: $ZipPath"
}
else {
    Write-Host "  ZIP:     $ZipPath"
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [System.IO.Compression.ZipFile]::OpenRead($ZipPath)
    try {
        $zipPaths = $zip.Entries |
            Where-Object { $_.FullName -notmatch '/$' } |
            ForEach-Object { $_.FullName.Replace("\", "/") } |
            Sort-Object

        $zipPayload = $zipPaths |
            Where-Object { $_ -match '^opengate/' } |
            ForEach-Object { $_.Substring("opengate/".Length) }

        foreach ($rel in $expected) {
            if ($zipPayload -notcontains $rel) {
                Add-Failure "Missing in ZIP: opengate/$rel"
            }
        }

        foreach ($entry in $zipPayload) {
            if ($expectedSet -notcontains $entry) {
                Add-Failure "Unexpected file in ZIP: opengate/$entry"
            }
        }

        foreach ($entry in $zipPaths) {
            foreach ($frag in $forbiddenZipFragments) {
                if ($entry -like "*$frag*") {
                    Add-Failure "Forbidden content in ZIP: $entry"
                }
            }
        }

        if ($zipPaths.Count -ne $expected.Count) {
            Add-Failure "ZIP file count mismatch: expected $($expected.Count), found $($zipPaths.Count)"
        }
    }
    finally {
        $zip.Dispose()
    }
}

if ($failures.Count -eq 0) {
    $fileCount = $expected.Count
    Write-Host "OK - repo and ZIP match release_inventory.txt ($fileCount files)."
    exit 0
}

Write-Host "FAILED - $($failures.Count) issue(s):" -ForegroundColor Red
foreach ($item in $failures) {
    Write-Host "  - $item" -ForegroundColor Red
}
exit 1

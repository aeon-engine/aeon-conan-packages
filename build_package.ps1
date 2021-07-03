function Prepare
{
    if (Test-Path "version.txt")
    {
        Remove-Item "version.txt"
    }

    conan config install remotes.txt

    $result = $LASTEXITCODE
    if ($result -ne 0)
    {
        throw "Failed to install conan remote config: $result"
    }

    conan user -p ${env:conan_api_key} -r aeon ${env:conan_api_user}

    $result = $LASTEXITCODE
    if ($result -ne 0)
    {
        echo "Warning: Failed to set conan credentials: $result"
    }

    $Env:CONAN_CPU_COUNT=4
}

function Build
{
    & ${env:python} build_package.py ${env:package_name}/${env:package_version}@${env:user_channel} -s build_type=${env:build_type}

    $result = $LASTEXITCODE
    if ($result -ne 0)
    {
        throw "Conan failed with exit code $result"
    }
}

function Deploy
{
    $package_version = [IO.File]::ReadAllText("version.txt")
    echo "Deploying $package_version"

    conan upload $package_version --all -r=aeon

    $result = $LASTEXITCODE
    if ($result -ne 0)
    {
        throw "Failed to set upload package: $result"
    }
}

Prepare
Build
Deploy

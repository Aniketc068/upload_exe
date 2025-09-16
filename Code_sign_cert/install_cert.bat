@echo off
REM Installing the PEM certificate into Trusted Root Certification Authorities
echo Installing certificate...

:: Embedding the certificate directly into the batch file
echo -----BEGIN CERTIFICATE----- > "%temp%\Managex_India_Certificate.pem"
echo MIIDQDCCAiigAwIBAgICA+gwDQYJKoZIhvcNAQELBQAwUTELMAkGA1UEBhMCSU4x >> "%temp%\Managex_India_Certificate.pem"
echo IDAeBgNVBAoMF01hbmFnZXggKElORElBKSBMaW1pdGVkMSAwHgYDVQQDDBdNYW5h >> "%temp%\Managex_India_Certificate.pem"
echo Z2V4IChJTkRJQSkgTGltaXRlZDAeFw0yNTA5MDUxMDU1NTZaFw0zNTA5MDMxMDU1 >> "%temp%\Managex_India_Certificate.pem"
echo NTZaMFExCzAJBgNVBAYTAklOMSAwHgYDVQQKDBdNYW5hZ2V4IChJTkRJQSkgTGlt >> "%temp%\Managex_India_Certificate.pem"
echo aXRlZDEgMB4GA1UEAwwXTWFuYWdleCAoSU5ESUEpIExpbWl0ZWQwggEiMA0GCSqG >> "%temp%\Managex_India_Certificate.pem"
echo SIb3DQEBAQUAA4IBDwAwggEKAoIBAQCstVMdXpSxd/Zuzc1kZgaKoAAHxMMfbNgl >> "%temp%\Managex_India_Certificate.pem"
echo 5SYuwf+QBhU/IjG855KhUUoDIq1rrBejuilM+VZgMm4HBj2lAEVwyKzs5Bm/fTaV >> "%temp%\Managex_India_Certificate.pem"
echo CCtzSt79vC0CPpWEZIl7bWlPg5uRuncaz1FscQNlktTIRYG5pyCY9ZYMPNfTfEG6 >> "%temp%\Managex_India_Certificate.pem"
echo 356gpa5GKwuoY3Bp86UOWEiL0BfF7TmAZJX3RqFbOdLxGCQHCeNAW/Z7eS92fEDq >> "%temp%\Managex_India_Certificate.pem"
echo PkDBfIHADKaJe7IdDLKu2hnMwrH+ixa0hWwayGDMQXxaBCete6LXPFF1mVYjMlMe >> "%temp%\Managex_India_Certificate.pem"
echo eZB1npCruH6jw9C1uQIPsEMktUXhVQ+CjyEmgp/HHatzkfzxFdjFAgMBAAGjIjAg >> "%temp%\Managex_India_Certificate.pem"
echo MB4GA1UdEQQXMBWCE3d3dy5tYW5hZ2V4aW5kaWEuaW4wDQYJKoZIhvcNAQELBQAD >> "%temp%\Managex_India_Certificate.pem"
echo ggEBABEMHEHMvZiwfHgC5CPkIvRDaEUgl82HPQWWQHX4YAwYzopnBqfiRCaDay9i >> "%temp%\Managex_India_Certificate.pem"
echo lpTXz+qZTZXNTHZ9ztFBAuL+7sYuZuyM5VRrAonk/u+Of9edgdozej2GhoZMYLCP >> "%temp%\Managex_India_Certificate.pem"
echo yLywxTveEwlfetuvkjvJZgX9u6FZd/Rdl8ssij0nrvgCQ18vJ197LDpiKDkSSeQT >> "%temp%\Managex_India_Certificate.pem"
echo EsO5ta9ZGvh+bTpgtA8Eo9Etu5ot5ww015VqcHc65Wwl9bVe+ZLKzhcmRJ/JMWi+ >> "%temp%\Managex_India_Certificate.pem"
echo 66rbqA6qvLxGLBmqyGfXoDTUT6hhHgnMwjH6JasCNJpzPNy9EY+8O+66wwdvLnGd >> "%temp%\Managex_India_Certificate.pem"
echo bEvXROVMmvIJmI7/7SSIRwn6K3g= >> "%temp%\Managex_India_Certificate.pem"
echo -----END CERTIFICATE----- >> "%temp%\Managex_India_Certificate.pem"

REM Install the certificate
certutil -addstore "Root" "%temp%\Managex_India_Certificate.pem"

REM Cleanup the temporary PEM file
del "%temp%\Managex_India_Certificate.pem"

REM Close automatically after installation
exit

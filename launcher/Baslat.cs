// Elden Ring Türkçe yama başlatıcısı.
// Tek işi: yanındaki me3\bin\me3.exe'yi EldenRing_TR.me3 profiliyle çalıştırmak.
// Oyun dosyalarına, exe'ye veya sisteme hiçbir şey yazmaz.
// Steam Başlatma Seçenekleri'nden "%command%" ile çağrılırsa gelen argümanlar yok sayılır.
using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

[assembly: System.Reflection.AssemblyTitle("Elden Ring Türkçe Yama Başlatıcı")]
[assembly: System.Reflection.AssemblyDescription("Elden Ring'i Türkçe yama ile me3 üzerinden başlatır")]
[assembly: System.Reflection.AssemblyProduct("Elden Ring Türkçe Yama")]
[assembly: System.Reflection.AssemblyCopyright("Açık kaynak - ücretsiz")]
[assembly: System.Reflection.AssemblyVersion("1.0.0.0")]
[assembly: System.Reflection.AssemblyFileVersion("1.0.0.0")]

static class Baslat
{
    const string Baslik = "Elden Ring Türkçe Yama";

    [STAThread]
    static int Main()
    {
        string klasor = AppDomain.CurrentDomain.BaseDirectory;
        string me3 = Path.Combine(klasor, @"me3\bin\me3.exe");
        string profil = Path.Combine(klasor, "EldenRing_TR.me3");

        if (!File.Exists(me3))
            return Hata("me3 bulunamadı:\n" + me3 + "\n\nArşivdeki tüm dosyaları aynı klasöre çıkardığından emin ol.");
        if (!File.Exists(profil))
            return Hata("Profil dosyası bulunamadı:\n" + profil);

        var bilgi = new ProcessStartInfo(me3, "launch -p \"" + profil + "\" -g eldenring")
        {
            WorkingDirectory = klasor,
            UseShellExecute = false,
            CreateNoWindow = true,
        };

        try
        {
            using (var p = Process.Start(bilgi))
            {
                // me3 hemen hata verip kapanırsa kullanıcıya göster.
                if (p.WaitForExit(15000) && p.ExitCode != 0)
                    return Hata("Oyun başlatılamadı (me3 hata kodu " + p.ExitCode + ").\n\n" +
                                "Steam açık mı, oyun kurulu mu kontrol et; olmazsa OKU_BENI_KURULUM.txt\n" +
                                "içindeki PowerShell yöntemini dene, orada hata mesajı görünür.");
            }
        }
        catch (Exception e)
        {
            return Hata("Oyun başlatılamadı:\n" + e.Message);
        }
        return 0;
    }

    static int Hata(string mesaj)
    {
        MessageBox.Show(mesaj, Baslik, MessageBoxButtons.OK, MessageBoxIcon.Error);
        return 1;
    }
}

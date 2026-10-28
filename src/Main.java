import java.awt.Desktop;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

/** Inicia el servidor Django de la tienda desde IntelliJ. */
public class Main {
    private static final String PAGE_URL = "http://127.0.0.1:8000/";

    public static void main(String[] args) {
        Path project = findProjectDirectory();
        if (project == null) {
            System.err.println("No encuentro manage.py. Configura la carpeta de trabajo de IntelliJ en la raiz del proyecto.");
            return;
        }

        List<List<String>> commands = pythonCommands(project);
        for (List<String> command : commands) {
            try {
                Process migration = new ProcessBuilder(command.get(0), "manage.py", "migrate", "--noinput")
                        .directory(project.toFile())
                        .inheritIO()
                        .start();

                if (migration.waitFor() != 0) {
                    System.err.println("No se pudieron preparar las tablas de la base de datos. Revisa el error de Django mostrado arriba.");
                    return;
                }

                ProcessBuilder serverBuilder = new ProcessBuilder(command)
                        .directory(project.toFile())
                        .inheritIO();
                serverBuilder.environment().putIfAbsent("DJANGO_DEBUG", "true");
                Process server = serverBuilder.start();

                System.out.println("Iniciando el servidor de la pagina...");
                if (waitForPage(server)) {
                    openPageInBrowser();
                }

                int exitCode = server.waitFor();
                if (exitCode != 0) {
                    System.err.println("Django termino con el codigo " + exitCode + ". Revisa el error mostrado arriba.");
                }
                return;
            } catch (IOException e) {
                // Prueba el siguiente nombre habitual del ejecutable de Python.
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                System.err.println("El inicio del servidor fue interrumpido.");
                return;
            }
        }

        System.err.println("No se encontro un ejecutable de Python disponible.");
        System.err.println("Instala Python o crea .venv en la raíz del proyecto.");
        System.err.println("Luego instala las dependencias con: python -m pip install -r requirements.txt");
    }

    private static List<List<String>> pythonCommands(Path project) {
        List<List<String>> commands = new ArrayList<>();
        Path venvPython = project.resolve(".venv").resolve("Scripts").resolve("python.exe");
        if (Files.isRegularFile(venvPython)) {
            commands.add(List.of(venvPython.toString(), "manage.py", "runserver", "127.0.0.1:8000"));
        }
        commands.add(List.of("python", "manage.py", "runserver", "127.0.0.1:8000"));
        commands.add(List.of("py", "-3", "manage.py", "runserver", "127.0.0.1:8000"));
        commands.add(List.of("python3", "manage.py", "runserver", "127.0.0.1:8000"));
        return commands;
    }

    private static Path findProjectDirectory() {
        Path directory = Path.of(System.getProperty("user.dir")).toAbsolutePath();
        while (directory != null) {
            if (Files.isRegularFile(directory.resolve("manage.py"))) {
                return directory;
            }
            directory = directory.getParent();
        }
        return null;
    }

    private static boolean waitForPage(Process process) throws InterruptedException {
        for (int attempt = 0; attempt < 60 && process.isAlive(); attempt++) {
            HttpURLConnection connection = null;
            try {
                connection = (HttpURLConnection) new URL(PAGE_URL).openConnection();
                connection.setConnectTimeout(500);
                connection.setReadTimeout(500);
                connection.setRequestMethod("GET");
                int status = connection.getResponseCode();
                if (status >= 200 && status < 400) {
                    return true;
                }
            } catch (IOException ignored) {
                // Django sigue iniciando; vuelve a intentar.
            } finally {
                if (connection != null) {
                    connection.disconnect();
                }
            }

            Thread.sleep(500);
        }

        if (process.isAlive()) {
            System.err.println("El servidor tardo en responder. Abre manualmente " + PAGE_URL);
        }
        return false;
    }

    private static void openPageInBrowser() {
        URI page = URI.create(PAGE_URL);
        try {
            if (Desktop.isDesktopSupported() && Desktop.getDesktop().isSupported(Desktop.Action.BROWSE)) {
                Desktop.getDesktop().browse(page);
                System.out.println("Pagina abierta en el navegador.");
            } else {
                System.out.println("Abre la página en " + PAGE_URL);
            }
        } catch (IOException e) {
            System.err.println("No pude abrir el navegador automáticamente. Abre " + PAGE_URL);
        }
    }
}
t
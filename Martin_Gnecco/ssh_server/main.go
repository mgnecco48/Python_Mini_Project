package main

import (
	"context"
	"errors"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/joho/godotenv"

	"charm.land/log/v2"
	"charm.land/ssh"
	"charm.land/wish/v2"
	"charm.land/wish/v2/activeterm"
	"charm.land/wish/v2/logging"
)

func main() {

	_ = godotenv.Load()

	host := os.Getenv("HOST")
	port := os.Getenv("PORT")

	pythonPath := os.Getenv("PYTHON_PATH")
	gamePath := os.Getenv("GAME_PATH")
	projectPath := os.Getenv("PROJECT_PATH")

	srv, err := wish.NewServer(
		wish.WithAddress(net.JoinHostPort(host, port)),
		wish.WithHostKeyPath(".ssh/id_ed25519"),

		// Allocate a PTY for each SSH session.
		ssh.AllocatePty(),

		wish.WithMiddleware(
			func(next ssh.Handler) ssh.Handler {
				return func(sess ssh.Session) {
					cmd := wish.Command(
						sess,
						pythonPath,
						gamePath,
					)

					cmd.SetDir(projectPath)

					if err := cmd.Run(); err != nil {
						wish.Printf(sess, "game failed: %v\r\n", err)
						_ = sess.Exit(1)
						return
					}

					_ = sess.Exit(0)
				}
			},

			activeterm.Middleware(),
			logging.Middleware(),
		),
	)

	if err != nil {
		log.Fatal("Could not create server", "error", err)
	}

	done := make(chan os.Signal, 1)

	signal.Notify(
		done,
		os.Interrupt,
		syscall.SIGINT,
		syscall.SIGTERM,
	)

	go func() {
		log.Info(
			"Starting SSH server",
			"host",
			host,
			"port",
			port,
		)

		if err := srv.ListenAndServe(); err != nil &&
			!errors.Is(err, ssh.ErrServerClosed) {

			log.Error(
				"Could not start server",
				"error",
				err,
			)

			done <- syscall.SIGTERM
		}
	}()

	<-done

	log.Info("Stopping SSH server")

	ctx, cancel := context.WithTimeout(
		context.Background(),
		30*time.Second,
	)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil &&
		!errors.Is(err, ssh.ErrServerClosed) {

		log.Error(
			"Could not stop server",
			"error",
			err,
		)
	}
}

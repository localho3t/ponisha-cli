from plyer import notification


class Notif:
    def __init__(self,message,status):
        self.message = message
        self.status = status
        self.__exec()

    def __exec(self):
        if (self.status == 1):
            notification.notify(
                title="یادآوری",
                message=f"{self.message}",
                app_name="[Ponisha]",
                timeout=5
            )
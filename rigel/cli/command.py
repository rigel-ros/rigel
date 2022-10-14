import click
import inspect
from typing import Any, Callable, Optional


class CLICommand():

    def __init__(self, command: Optional[str] = None) -> None:

        self.__click_group = click.Group()
        self.__click_group.name = command or self.__class__.__name__.lower()
        self.__click_group.help = self.__class__.__dict__.get('__doc__')

        # Replace original callbacks with caller objects to support 'self'
        for name, command in inspect.getmembers(self):
            if isinstance(command, click.Command):
                if command.callback:
                    command.callback = self.__generate_callback(command.callback)
                    self.__click_group.add_command(command, name)

    def __generate_callback(self, f: Callable) -> Callable[[Any, Any], None]:
        def callback(*f_args: Any, **f_kwargs: Any) -> None:
            f(self, *f_args, **f_kwargs)
        return callback

    def add_to_group(self, group: click.Group) -> None:
        group.add_command(self.__click_group)

# if __name__ == '__main__':

#     class GreeterCommand(CLICommand):
#         """ Speak to an user
#         """

#         def __init__(self, name: str, age: int):
#             super().__init__(command='greet')
#             self.name = name
#             self.age = age

#         @click.command()
#         @click.argument('name', type=str)
#         def hello(self, name: str) -> None:
#             """Greet user"""
#             print(f'Hello {name}, my name is {self.name} and I am {self.age} years old.')

#     # ==================================================================

#     cli = click.Group()
#     GreeterCommand('Bot Fred', 42).add_to_group(cli)
#     cli()

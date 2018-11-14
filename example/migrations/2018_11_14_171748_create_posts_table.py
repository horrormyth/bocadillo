from orator.migrations import Migration


class CreatePostsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('posts') as table:
            table.increments('id')
            table.timestamps()
            table.char('title', 128)
            table.char('slug', 128)
            table.string('content')

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('posts')

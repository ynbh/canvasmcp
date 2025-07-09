
import { tool } from "ai";
import { listTodoItemsDataSchema } from "./aitm.schema.ts";
import { listTodoItems, ListTodoItemsData } from "..";

export default tool({
  description: `
  List the TODO items
A paginated list of the current user's list of todo items, as seen on the user
dashboard.

There is a limit to the number of items returned.

The `ignore` and `ignore_permanently`
URLs can be used to update the user's
preferences on what items will be displayed.
Performing a
DELETE request against the `ignore` URL will hide that item
from future todo item requests, until
the item changes.
Performing a DELETE request against the `ignore_permanently` URL will hide
that
item forever.
    `,
  parameters: listTodoItemsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListTodoItemsData, "url"> ) => {
    try {
      const { data } = await listTodoItems(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    

import { tool } from "ai";
import { findRecipientsSearchDataSchema } from "./aitm.schema.ts";
import { findRecipientsSearch, FindRecipientsSearchData } from "..";

export default tool({
  description: `
  Find recipients
Find valid recipients (users, courses and groups) that the current user
can send
messages to. The /api/v1/search/recipients path is the preferred
endpoint,
/api/v1/conversations/find_recipients is deprecated.

Pagination is supported.
    `,
  parameters: findRecipientsSearchDataSchema.omit({ url: true }),
  execute: async (args : Omit<FindRecipientsSearchData, "url"> ) => {
    try {
      const { data } = await findRecipientsSearch(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
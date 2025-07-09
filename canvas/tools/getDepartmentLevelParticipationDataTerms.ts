
import { tool } from "ai";
import { getDepartmentLevelParticipationDataTermsDataSchema } from "./aitm.schema.ts";
import { getDepartmentLevelParticipationDataTerms, GetDepartmentLevelParticipationDataTermsData } from "..";

export default tool({
  description: `
  Get department-level participation data
Returns page view hits summed across all courses in the
department. Two
groupings of these counts are returned; one by day (+by_date+), the other
by
category (+by_category+). The possible categories are announcements,
assignments, collaborations,
conferences, discussions, files, general,
grades, groups, modules, other, pages, and quizzes.

This
and the other department-level endpoints have three variations which
all return the same style of
data but for different subsets of courses. All
share the prefix
/api/v1/accounts/<account_id>/analytics. The possible
suffixes are:

* /current: includes all
available courses in the default term
* /completed: includes all concluded courses in the default
term
* /terms/<term_id>: includes all available or concluded courses in the
given term.

Courses not
yet offered or which have been deleted are never included.

/current and /completed are intended for
use when the account has only one
term. /terms/<term_id> is intended for use when the account has
multiple
terms.

The action follows the suffix.
    `,
  parameters: getDepartmentLevelParticipationDataTermsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetDepartmentLevelParticipationDataTermsData, "url"> ) => {
    try {
      const { data } = await getDepartmentLevelParticipationDataTerms(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
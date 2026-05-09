# Code Review — PR #4577: Migrate `UserRepository` from JDBC to JPA

## Verdict: REQUEST_CHANGES (2 blocking, 3 suggestions, 4 nits, 2 praise)

Reviewer-coverage: persistence semantics + transaction boundaries + N+1 risk. Not covered: schema-migration rollback path (covered by `/migrate` verdict on the same change).

## Findings

### `UserRepository.java:51` — issue (blocking, correctness)

issue (blocking): `findActiveUsers()` runs without `@Transactional`. The JPA EntityManager will close mid-iteration and `LazyInitializationException` will surface in production. JDBC version was implicitly transactional via the `Connection`. Add `@Transactional(readOnly = true)`.

### `UserRepository.java:79` — issue (blocking, performance)

issue (blocking, N+1): `users.forEach(u -> u.getRoles().size())` triggers N+1 queries per call. Use `JOIN FETCH` in the JPQL or `@EntityGraph(attributePaths = "roles")`. Measured: 1 → 1 + N queries on the `findManagers()` benchmark.

### `UserRepository.java:104` — suggestion (non-blocking)

suggestion: move `findByEmail` to a derived-query method (`Optional<User> findByEmail(String email)`) and let Spring Data generate the JPQL. The hand-written `@Query` is identical to the auto-generated one.

### `UserRepositoryTest.java:42` — suggestion (non-blocking)

suggestion: prefer `@DataJpaTest` slice over full `@SpringBootTest` for repository tests. ~3× faster startup.

### `UserMapper.java:28` — suggestion (non-blocking)

suggestion (testing): the mapper has no test covering the new `roles` field. Add a parity test — easy to forget across the migration.

### `UserRepository.java:11` — nit (non-blocking)

nit (typo): `Repostiory` in the class-level Javadoc.

### `UserRepository.java:40` — nit (non-blocking)

nit: import order — `org.springframework.*` should precede `com.example.*` per project checkstyle.

### `UserRepositoryTest.java:18` — nit (non-blocking)

nit: prefer `assertThat().isPresent()` over `assertTrue(opt.isPresent())` — fluent assertions improve failure messages.

### `UserMapper.java:12` — nit (non-blocking)

nit: remove unused import `java.util.Date`.

### `UserRepository.java:94` — praise

praise: extracting `UserSearchSpec` as a Specification keeps the dynamic-where logic testable in isolation. Good call.

### `UserRepositoryTest.java:88` — praise

praise: parameterized test over the eight role-combinations is exactly the safety net this migration needs.

## Summary

2 blocking, 3 suggestions, 4 nits, 2 praise. Blocking items are transaction-scope and N+1 — both correctness/performance, both well-known JPA pitfalls. Code-health-over-perfection: nits and suggestions should not delay merge once blockers land.

Defer to siblings: schema rollback verification → `/migrate` (already in flight).

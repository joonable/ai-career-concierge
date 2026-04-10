"use client";

import Link from "next/link";

type WovenLightHeroProps = {
  headlineClassName: string;
  bodyClassName: string;
};

const HEADLINE = "AI Career Concierge";
const SUBCOPY = "정말 검토할 가치가 있는 공고만 남깁니다.";

export function WovenLightHero({
  headlineClassName,
  bodyClassName,
}: WovenLightHeroProps) {
  const words = HEADLINE.split(" ");

  return (
    <section className="woven-hero">
      <div className="woven-hero__veil" />

      <nav className="woven-nav">
        <div className="woven-nav__brand">
          <span className="woven-nav__mark" aria-hidden="true">
            ⎎
          </span>
          <span className={bodyClassName}>AI Career Concierge</span>
        </div>
      </nav>

      <div className="woven-hero__content">
        <h1 className={`woven-hero__headline ${headlineClassName}`}>
          {words.map((word, wordIndex) => (
            <span className="woven-hero__word" key={word}>
              {word.split("").map((char, charIndex) => (
                <span key={`${word}-${charIndex}`} className="woven-hero__char">
                  {char}
                </span>
              ))}
              {wordIndex < words.length - 1 ? <span>&nbsp;</span> : null}
            </span>
          ))}
        </h1>

        <p className={`woven-hero__subcopy ${bodyClassName}`}>
          {SUBCOPY}
        </p>

        <div className="woven-hero__cta-wrap">
          <Link className={`woven-hero__cta ${bodyClassName}`} href="/login">
            로그인
          </Link>
        </div>
      </div>
    </section>
  );
}
